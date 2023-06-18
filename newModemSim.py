import numpy as np

Fs = 48000 #Hz
ToneFreq = 1023 #Hz
volume = 1.0
duration = 1 #sec
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

#for i in range(0,len(finalMappedData)):
    #create sync marker
    
    #append time domain data from IFFT

    #mix up and upsample to audio data rates (48000 samples per second)

    #add packet to packet buffer

#end for

#transmit packets !NOT A REAL STEP! Just plot it and wait



