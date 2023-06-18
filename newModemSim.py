import numpy as np

Fs = 48000 #Hz
ToneFreq = 1023 #Hz
volume = 1.0
duration = 0.1 #sec
#16bit signed audio

#generate data
debugX = []
debugYLeft = []
debugYRight = []
for i in range(0,int((duration//(1/Fs)))): #should be 960
    time = (1/Fs)*i
    voltageLeft = np.cos(time * ToneFreq) * ((2**15) * (volume))
    voltageRight = np.sin(time * ToneFreq) * ((2**15) * (volume))

    voltageLeft = int(voltageLeft)
    voltageRight = int(voltageRight)

    #Clip
    if voltageLeft >= (2**15) - 1:
        voltageLeft = (2**15) - 1
    elif voltageLeft <= -2**15:
        voltageLeft = -2**15
    #Clip
    if voltageRight >= (2**15) - 1:
        voltageRight = (2**15) - 1
    elif voltageRight <= -2**15:
        voltageRight = -2**15

    debugX.append(time)
    debugYLeft.append(voltageLeft)
    debugYRight.append(voltageRight)

rawDataPackets = []
#packetize data // Assume 64 point IFFT // We will map two 16 bit audio samples to 1 OFDM frame (left and right stereo)
for i in range(0,len(debugYLeft)):
    rawDataPackets.append([debugYLeft[i],debugYRight[i]])



def MapStereoAudioData(numOfPoints, bitWidth, leftSample, rightSample):
    numOfPoints = int(numOfPoints)
    bitWidth = int(bitWidth)
    leftSample = int(leftSample)
    rightSample = int(rightSample)
    
    numOfPointsAllowed = []
    
    for i in range(1,65):
        numOfPointsAllowed.append(2**i)
    
    proceed = False
    
    for i in numOfPointsAllowed:
        if (numOfPoints == i):
            proceed = True
    if (proceed == False):
        raise Exception("MapStereoAudioData: Conditions not met")

    #Generate Mask
    maskToUse = 0x1
    maskToUse  = maskToUse << (bitWidth - 1)
    leftMask = maskToUse
    rightMask = maskToUse
    
    mappedData = []
    for i in range(0,numOfPoints):
        mappedData.append(np.complex(0,0))
        
    for i in range(1,bitWidth + 1): #skip Fs/2, left audio channel, negative frequencies
        if ((leftSample & leftMask) == leftMask):
            mappedData[i] = np.complex(1,1)
        else:
            mappedData[i] = np.complex(-1,-1)
        leftMask = leftMask >> 1
    for i in range(((numOfPoints//2) + 1),(numOfPoints//2) + 1 + bitWidth): #skip DC, right audio channel, positive frequencies
        if ((rightSample & rightMask) == rightMask):
            mappedData[i] = np.complex(1,1)
        else:
            mappedData[i] = np.complex(-1,-1)
        rightMask = rightMask >> 1
        
    mappedData[numOfPoints//2] = np.complex(1,1) #DC set to full power in phase
    
    mappedData = np.fft.fftshift(mappedData)
    
    return mappedData

def StringListOfListsSamplesTogether(listOflistsOfSamples):
    masterList = []
    for i in listOflistsOfSamples:
        for j in i:
            masterList.append(j)
    return masterList

#map packets to carriers
#64 point IFFT yields frequency bins -31 - +32
#0 will be a pilot tone to estimate phase offset
#-16 to -1 will be stereo left
#1 to 16 will be stereo right
#No intentional phase shift represent 1's, intentional phase shifts represent 0's
#Arrangement of data is the following
#a[0] should contain the zero frequency term,
#a[1:n//2] should contain the positive-frequency terms,
#a[n//2 + 1:] should contain the negative-frequency terms, in increasing order starting from the most negative frequency.
finalMappedData = []
for i in range(0,len(rawDataPackets)):        
    finalMappedData.append(MapStereoAudioData(64,16,rawDataPackets[i][0],rawDataPackets[i][1]).copy())


#Generate Sync Marker
thirteenBitBarker = [1,1,1,1,1,-1,-1,1,1,-1,1,-1,1]
transformedThirteenBitBarker = []
syncMarkerTimeDomainSamples = []
for i in thirteenBitBarker:
    if (i == 1):
        transformedThirteenBitBarker.append(0xFFFF)
    else:
        transformedThirteenBitBarker.append(0x0000)
        
syncMarkerData = []
for i in range(0,16): #0 is preamble, 1-13 is Barker, 14-15 is postamble
    if (i == 0): #preamble
        syncMarkerData.append(MapStereoAudioData(64,16,0xFFFF,0xFFFF))
    elif ((i >= 1) & (i <= 13)):
        syncMarkerData.append(MapStereoAudioData(64,16,transformedThirteenBitBarker[i-1],transformedThirteenBitBarker[i-1]))
    elif ((i == 14) | (i == 15)):
        syncMarkerData.append(MapStereoAudioData(64,16,0xFFFF,0xFFFF))
    else:
        raise Exception("GenerateSyncMarker: Index out of range")

for i in range(0,len(syncMarkerData)):
    syncMarkerTimeDomainSamples.append(np.fft.ifft(syncMarkerData[i],64))

timeBetweenPackets = 0.001 #seconds
numberOfSamplePairsPerPacket = 10
packetsOfTimeDomainData = []
dataPointer = 0
while (dataPointer < len(finalMappedData)):
    tempTimeDomainData = []
    #apply sync marker and time domain data from digitally represented audio data
    tempTimeDomainData.append(StringListOfListsSamplesTogether(syncMarkerTimeDomainSamples).copy())
    for i in range(0,numberOfSamplePairsPerPacket):
        if ((dataPointer + i) < len(finalMappedData)):
            tempTimeDomainData.append(np.fft.ifft(finalMappedData[dataPointer + i],64))
            dataPointer += 1
    packetsOfTimeDomainData.append(StringListOfListsSamplesTogether(tempTimeDomainData).copy())


fsOfDataToTransmit = 4e3 #Hz
#mix up and upsample to audio data rates (48000 samples per second)
#define 1.960 kHz wide (1.960*2 kHz complex) 400 Hz stopband LPF
#blackmann https://fiiir.com/
h = [
    0.000000000000000000,
    0.000000919129687293,
    -0.000004501780353382,
    0.000012086923486771,
    -0.000025174126626167,
    0.000045453726193954,
    -0.000074832601165571,
    0.000115453419243375,
    -0.000169705369133180,
    0.000240224621958502,
    -0.000329883075871759,
    0.000441764321437684,
    -0.000579126209371202,
    0.000745349892180907,
    -0.000943875730620484,
    0.001178126986507323,
    -0.001451422746481630,
    0.001766882017483201,
    -0.002127321385417352,
    0.002535149016100835,
    -0.002992258086338898,
    0.003499922949471680,
    -0.004058701453411972,
    0.004668346832855857,
    -0.005327732487378934,
    0.006034792733740872,
    -0.006786482287985593,
    0.007578756798716029,
    -0.008406576228702660,
    0.009263932282477830,
    -0.010143900420298163,
    0.011038716303619064,
    -0.011939875805426811,
    0.012838257012755630,
    -0.013724261971008627,
    0.014587975292270430,
    -0.015419336193317142,
    0.016208320062165330,
    -0.016945125290779798,
    0.017620360868826599,
    -0.018225230118269944,
    0.018751705966396515,
    -0.019192693306500870,
    0.019542174277751137,
    -0.019795332701286555,
    0.019948654426992275,
    0.980000047026855059,
    0.019948654426992275,
    -0.019795332701286559,
    0.019542174277751137,
    -0.019192693306500870,
    0.018751705966396515,
    -0.018225230118269944,
    0.017620360868826599,
    -0.016945125290779801,
    0.016208320062165327,
    -0.015419336193317142,
    0.014587975292270433,
    -0.013724261971008627,
    0.012838257012755634,
    -0.011939875805426811,
    0.011038716303619070,
    -0.010143900420298170,
    0.009263932282477827,
    -0.008406576228702662,
    0.007578756798716031,
    -0.006786482287985591,
    0.006034792733740875,
    -0.005327732487378931,
    0.004668346832855859,
    -0.004058701453411973,
    0.003499922949471680,
    -0.002992258086338900,
    0.002535149016100838,
    -0.002127321385417353,
    0.001766882017483200,
    -0.001451422746481631,
    0.001178126986507324,
    -0.000943875730620485,
    0.000745349892180907,
    -0.000579126209371202,
    0.000441764321437685,
    -0.000329883075871759,
    0.000240224621958502,
    -0.000169705369133180,
    0.000115453419243375,
    -0.000074832601165571,
    0.000045453726193954,
    -0.000025174126626167,
    0.000012086923486771,
    -0.000004501780353382,
    0.000000919129687293,
    0.000000000000000000]

lowPassFilteredPacketsOfTimeDomainData = []
for i in range(0,len(packetsOfTimeDomainData)):
    lowPassFilteredPacketsOfTimeDomainData.append(np.convolve(packetsOfTimeDomainData[i], h))

#generate mixing cosinewave


#end for

#transmit packets !NOT A REAL STEP! Just plot it and wait



