import numpy as np
import matplotlib.pyplot as plt
import wave
import struct

Fs = 48000 #Hz
ToneFreq = 1023 #Hz
volume = 1.0
duration = 0.01 #sec
#16bit signed audio

fsOfDataToTransmit = 4e3 #Hz

#generate data
debugX = []
debugYLeft = []
debugYRight = []
for i in range(0,int((duration//(1/Fs)))): #should be 960
    time = (1/Fs)*i
    voltageLeft = np.cos(2 * np.pi * time * ToneFreq) * ((2**15) * (volume))
    voltageRight = np.sin(2 * np.pi * time * ToneFreq) * ((2**15) * (volume))

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


def UpSampleByN(samples, n):
    #L-Fold Expander
    #https://www.ni.com/docs/en-US/bundle/labview-digital-filter-design-toolkit-api-ref/page/lvdfdtconcepts/dfd_interpolation.html
    pythonOrNumpy = True #True is python, False is numpy
    
    if (pythonOrNumpy == True):
        numOfZeroesBetweenSamples = n-1
        
        newSamples = []
        for i in range(0, len(samples)):
            newSamples.append(samples[i])
            for j in range(0, numOfZeroesBetweenSamples):
                newSamples.append(np.complex(0,0))
    else:
        raise Exception("I havent figured this out yet")
        
    return newSamples

def GenerateIQTone(frequency, amplitude, fslocal, numOfSamples):
    iqSamples = []
    
    if (amplitude > 1.0):
        raise Exception("GenerateIQTone: Amplitude greatrer than 1.0")
    if (amplitude < 0.0):
        raise Exception("GenerateIQTone: Amplitude less than 0.0")
        
    for i in range(0,numOfSamples):
        time = i * (1/fslocal)
        iqSamples.append(np.complex(np.cos(2 * np.pi * time * frequency) * (((2**15)-1) * (amplitude)),
                                    np.sin(2 * np.pi * time * frequency) * (((2**15)-1) * (amplitude)))) 
    return iqSamples
    
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
        
    for i in range(16,bitWidth + 1 + 16): #skip Fs/2 and guard channels, left audio channel, negative frequencies
        if ((leftSample & leftMask) == leftMask):
            mappedData[i] = np.complex(1,0)
        else:
            mappedData[i] = np.complex(-1,0)
        leftMask = leftMask >> 1
    for i in range(((numOfPoints//2) + 1),(numOfPoints//2) + 1 + bitWidth): #skip DC, right audio channel, positive frequencies
        if ((rightSample & rightMask) == rightMask):
            mappedData[i] = np.complex(1,0)
        else:
            mappedData[i] = np.complex(-1,0)
        rightMask = rightMask >> 1
        
    mappedData[numOfPoints//2] = np.complex(0,0) #DC set to no power
    
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

syncMarkerTimeDomainSamples = []
bitDuration = 0.001 #seconds
lengthOfOneBitInSamples = bitDuration // (1 / fsOfDataToTransmit)
lengthOfBarkerSequenceInSamples = int(13 * lengthOfOneBitInSamples)
for i in range(0,13):
    tempSyncMarkerTimeDomainSamples = []
    for j in range(0, int(lengthOfOneBitInSamples)):
        tempSyncMarkerTimeDomainSamples.append(thirteenBitBarker[i])
    syncMarkerTimeDomainSamples.append(tempSyncMarkerTimeDomainSamples.copy())

"""
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
"""




numberOfSamplePairsPerPacket = 64
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



#upsample, LPF and mix up to 8kHz at audio data rates (48000 samples per second)

#upsample from 4000 Hz to 48000 Hz
#48000/4000 = 12 so insert 11 zeroes between every sample
for i in range(0, len(packetsOfTimeDomainData)):
    packetsOfTimeDomainData[i] = UpSampleByN(packetsOfTimeDomainData[i], 12).copy()

#define 2.0 kHz wide (2.0*2 kHz complex) 480 Hz stopband LPF
#blackmann https://fiiir.com/
h = [
    0.000000000000000000,
    -0.000000006041276169,
    0.000000000000000000,
    0.000000054880080055,
    0.000000189403438110,
    0.000000420640785826,
    0.000000745717744344,
    0.000001138157757944,
    0.000001547497242313,
    0.000001902531125997,
    0.000002118127491509,
    0.000002105112844725,
    0.000001782319999948,
    0.000001089553258721,
    0.000000000000000000,
    -0.000001469465576203,
    -0.000003251563968541,
    -0.000005226714214097,
    -0.000007226805728522,
    -0.000009044969423979,
    -0.000010451083681454,
    -0.000011212126133670,
    -0.000011115887483011,
    -0.000009996058934810,
    -0.000007756346406974,
    -0.000004391099143431,
    0.000000000000000000,
    0.000005205336519614,
    0.000010904481275703,
    0.000016681910485047,
    0.000022051327337954,
    0.000026489607370364,
    0.000029478406445217,
    0.000030550567792246,
    0.000029337730690574,
    0.000025615058114012,
    0.000019338828912682,
    0.000010672824876121,
    0.000000000000000000,
    -0.000012083166625094,
    -0.000024791008633494,
    -0.000037191618173608,
    -0.000048266730566032,
    -0.000056985286113505,
    -0.000062385942201357,
    -0.000063662605215997,
    -0.000060246232964497,
    -0.000051875825515245,
    -0.000038651744987994,
    -0.000021065311849166,
    0.000000000000000000,
    0.000023298569275199,
    0.000047284364621803,
    0.000070202433361495,
    0.000090205595321160,
    0.000105489375051049,
    0.000114436138597390,
    0.000115757881939668,
    0.000108626313380124,
    0.000092778903468225,
    0.000068590507981498,
    0.000037101999771730,
    0.000000000000000000,
    -0.000040454866567897,
    -0.000081549963763357,
    -0.000120287644658858,
    -0.000153588102996940,
    -0.000178515405134693,
    -0.000192511231081261,
    -0.000193619035851596,
    -0.000180680724264278,
    -0.000153488651116482,
    -0.000112877857905729,
    -0.000060746876301910,
    0.000000000000000000,
    0.000065590618222328,
    0.000131598704494626,
    0.000193223008390757,
    0.000245615690575837,
    0.000284238873462708,
    0.000305224610153457,
    0.000305711481936153,
    0.000284130877888561,
    0.000240417884211273,
    0.000176125612787700,
    0.000094427570283368,
    -0.000000000000000001,
    -0.000101215431404539,
    -0.000202359245383573,
    -0.000296093816834274,
    -0.000375108735961330,
    -0.000432658832857389,
    -0.000463097187283274,
    -0.000462363316166317,
    -0.000428387437138355,
    -0.000361375376834930,
    -0.000263945241589124,
    -0.000141096087819346,
    0.000000000000000003,
    0.000150378500082869,
    0.000299818777828659,
    0.000437506641114664,
    0.000552782461249821,
    0.000635925353780715,
    0.000678918191658192,
    0.000676136233288464,
    0.000624904261041547,
    0.000525873430077817,
    0.000383179304995321,
    0.000204356287430247,
    -0.000000000000000001,
    -0.000216812862470649,
    -0.000431319405453825,
    -0.000628034998395152,
    -0.000791827178110895,
    -0.000909027361399442,
    -0.000968501840670725,
    -0.000962601988326659,
    -0.000887917808473160,
    -0.000745768961073097,
    -0.000542382733461444,
    -0.000288728321089034,
    0.000000000000000001,
    0.000305233184566268,
    0.000606168452787630,
    0.000881134882770453,
    0.001109097519222869,
    0.001271199242629788,
    0.001352231435876441,
    0.001341923725080524,
    0.001235950206387662,
    0.001036564498101858,
    0.000752798004137242,
    0.000400183715797837,
    -0.000000000000000002,
    -0.000421936980883646,
    -0.000836869660146646,
    -0.001214990543158870,
    -0.001527509003439432,
    -0.001748754854639125,
    -0.001858170354629944,
    -0.001842042630805915,
    -0.001694839464603343,
    -0.001420032682175519,
    -0.001030324055057070,
    -0.000547226887997853,
    0.000000000000000002,
    0.000576023261902292,
    0.001141623158100314,
    0.001656269856561038,
    0.002080924884522512,
    0.002380880593681251,
    0.002528438471306414,
    0.002505228630671950,
    0.002303988387263600,
    0.001929647041293951,
    0.001399605424640571,
    0.000743150083271894,
    -0.000000000000000002,
    -0.000781955257175168,
    -0.001549607303863708,
    -0.002248097664383797,
    -0.002824585726834012,
    -0.003232066559246686,
    -0.003432973525290243,
    -0.003402302733171730,
    -0.003130016911458586,
    -0.002622524749099926,
    -0.001903086210421061,
    -0.001011061788071616,
    0.000000000000000002,
    0.001065362214161833,
    0.002113032563018472,
    0.003068404214119972,
    0.003859318699083437,
    0.004421222190441001,
    0.004702063914590680,
    0.004666585984414975,
    0.004299678484785901,
    0.003608521624174201,
    0.002623305953790016,
    0.001396408294296979,
    -0.000000000000000003,
    -0.001477830616141299,
    -0.002938255297485992,
    -0.004277899001649555,
    -0.005395683517747539,
    -0.006199894121994021,
    -0.006615005768089430,
    -0.006587798376312791,
    -0.006092314699250995,
    -0.005133268721400448,
    -0.003747595282663877,
    -0.002003938340204385,
    0.000000000000000003,
    0.002142192243158732,
    0.004282905087140227,
    0.006272879915788011,
    0.007962632650729259,
    0.009212339082000190,
    0.009901709585121812,
    0.009939230125260528,
    0.009270157654254835,
    0.007882708087879208,
    0.005811962219231351,
    0.003141134980351238,
    -0.000000000000000003,
    -0.003439573847906251,
    -0.006970843906713308,
    -0.010361871811734659,
    -0.013367197910499099,
    -0.015740915553575645,
    -0.017250444211914628,
    -0.017690234687324023,
    -0.016894617884166137,
    -0.014749033124495966,
    -0.011198942445888021,
    -0.006255850529578517,
    0.000000000000000003,
    0.007420509408332500,
    0.015794232015284498,
    0.024854367437236603,
    0.034289882066054364,
    0.043759228113076705,
    0.052905972510133147,
    0.061375530218738775,
    0.068832123418548566,
    0.074975064387658261,
    0.079553487494564534,
    0.082378733388551534,
    0.083333712000172810,
    0.082378733388551534,
    0.079553487494564534,
    0.074975064387658261,
    0.068832123418548566,
    0.061375530218738775,
    0.052905972510133147,
    0.043759228113076705,
    0.034289882066054364,
    0.024854367437236607,
    0.015794232015284498,
    0.007420509408332501,
    0.000000000000000003,
    -0.006255850529578518,
    -0.011198942445888023,
    -0.014749033124495967,
    -0.016894617884166137,
    -0.017690234687324023,
    -0.017250444211914628,
    -0.015740915553575645,
    -0.013367197910499099,
    -0.010361871811734657,
    -0.006970843906713308,
    -0.003439573847906251,
    -0.000000000000000003,
    0.003141134980351238,
    0.005811962219231352,
    0.007882708087879210,
    0.009270157654254835,
    0.009939230125260530,
    0.009901709585121814,
    0.009212339082000191,
    0.007962632650729259,
    0.006272879915788013,
    0.004282905087140228,
    0.002142192243158732,
    0.000000000000000003,
    -0.002003938340204385,
    -0.003747595282663878,
    -0.005133268721400450,
    -0.006092314699250995,
    -0.006587798376312791,
    -0.006615005768089427,
    -0.006199894121994020,
    -0.005395683517747539,
    -0.004277899001649556,
    -0.002938255297485992,
    -0.001477830616141299,
    -0.000000000000000003,
    0.001396408294296980,
    0.002623305953790017,
    0.003608521624174202,
    0.004299678484785902,
    0.004666585984414975,
    0.004702063914590681,
    0.004421222190441001,
    0.003859318699083437,
    0.003068404214119972,
    0.002113032563018472,
    0.001065362214161833,
    0.000000000000000002,
    -0.001011061788071617,
    -0.001903086210421062,
    -0.002622524749099926,
    -0.003130016911458586,
    -0.003402302733171732,
    -0.003432973525290245,
    -0.003232066559246687,
    -0.002824585726834012,
    -0.002248097664383797,
    -0.001549607303863708,
    -0.000781955257175168,
    -0.000000000000000002,
    0.000743150083271894,
    0.001399605424640571,
    0.001929647041293951,
    0.002303988387263599,
    0.002505228630671950,
    0.002528438471306414,
    0.002380880593681250,
    0.002080924884522514,
    0.001656269856561039,
    0.001141623158100315,
    0.000576023261902293,
    0.000000000000000002,
    -0.000547226887997852,
    -0.001030324055057071,
    -0.001420032682175520,
    -0.001694839464603344,
    -0.001842042630805916,
    -0.001858170354629944,
    -0.001748754854639126,
    -0.001527509003439433,
    -0.001214990543158870,
    -0.000836869660146646,
    -0.000421936980883646,
    -0.000000000000000002,
    0.000400183715797837,
    0.000752798004137243,
    0.001036564498101858,
    0.001235950206387663,
    0.001341923725080524,
    0.001352231435876441,
    0.001271199242629790,
    0.001109097519222869,
    0.000881134882770454,
    0.000606168452787630,
    0.000305233184566268,
    0.000000000000000001,
    -0.000288728321089034,
    -0.000542382733461445,
    -0.000745768961073097,
    -0.000887917808473161,
    -0.000962601988326658,
    -0.000968501840670725,
    -0.000909027361399443,
    -0.000791827178110895,
    -0.000628034998395152,
    -0.000431319405453825,
    -0.000216812862470649,
    -0.000000000000000001,
    0.000204356287430247,
    0.000383179304995322,
    0.000525873430077817,
    0.000624904261041547,
    0.000676136233288464,
    0.000678918191658192,
    0.000635925353780716,
    0.000552782461249820,
    0.000437506641114664,
    0.000299818777828659,
    0.000150378500082869,
    0.000000000000000003,
    -0.000141096087819345,
    -0.000263945241589124,
    -0.000361375376834929,
    -0.000428387437138355,
    -0.000462363316166317,
    -0.000463097187283274,
    -0.000432658832857389,
    -0.000375108735961330,
    -0.000296093816834274,
    -0.000202359245383573,
    -0.000101215431404539,
    -0.000000000000000001,
    0.000094427570283368,
    0.000176125612787700,
    0.000240417884211274,
    0.000284130877888561,
    0.000305711481936154,
    0.000305224610153457,
    0.000284238873462708,
    0.000245615690575837,
    0.000193223008390757,
    0.000131598704494626,
    0.000065590618222328,
    0.000000000000000000,
    -0.000060746876301910,
    -0.000112877857905729,
    -0.000153488651116482,
    -0.000180680724264278,
    -0.000193619035851596,
    -0.000192511231081261,
    -0.000178515405134693,
    -0.000153588102996940,
    -0.000120287644658858,
    -0.000081549963763357,
    -0.000040454866567897,
    0.000000000000000000,
    0.000037101999771730,
    0.000068590507981498,
    0.000092778903468226,
    0.000108626313380124,
    0.000115757881939668,
    0.000114436138597390,
    0.000105489375051049,
    0.000090205595321160,
    0.000070202433361495,
    0.000047284364621803,
    0.000023298569275199,
    0.000000000000000000,
    -0.000021065311849166,
    -0.000038651744987994,
    -0.000051875825515245,
    -0.000060246232964497,
    -0.000063662605215997,
    -0.000062385942201357,
    -0.000056985286113505,
    -0.000048266730566032,
    -0.000037191618173608,
    -0.000024791008633494,
    -0.000012083166625094,
    0.000000000000000000,
    0.000010672824876121,
    0.000019338828912682,
    0.000025615058114012,
    0.000029337730690574,
    0.000030550567792246,
    0.000029478406445217,
    0.000026489607370364,
    0.000022051327337954,
    0.000016681910485047,
    0.000010904481275703,
    0.000005205336519614,
    0.000000000000000000,
    -0.000004391099143431,
    -0.000007756346406974,
    -0.000009996058934810,
    -0.000011115887483011,
    -0.000011212126133670,
    -0.000010451083681454,
    -0.000009044969423979,
    -0.000007226805728522,
    -0.000005226714214097,
    -0.000003251563968541,
    -0.000001469465576203,
    0.000000000000000000,
    0.000001089553258721,
    0.000001782319999948,
    0.000002105112844725,
    0.000002118127491509,
    0.000001902531125997,
    0.000001547497242313,
    0.000001138157757944,
    0.000000745717744344,
    0.000000420640785826,
    0.000000189403438110,
    0.000000054880080055,
    0.000000000000000000,
    -0.000000006041276169,
    0.000000000000000000,
]

lowPassFilteredPacketsOfTimeDomainData = []
for i in range(0,len(packetsOfTimeDomainData)):
    lowPassFilteredPacketsOfTimeDomainData.append(np.convolve(packetsOfTimeDomainData[i], h))

#generate mixing cosinewave and upmix to real
upmixedSamples = []
for i in range(0,len(lowPassFilteredPacketsOfTimeDomainData)):
    complexMixingTone = []
    complexMixingTone = GenerateIQTone(6000, 1.0, 48000, len(lowPassFilteredPacketsOfTimeDomainData[i])).copy()
    tempUpmixedSamples = []
    for j in range(0, len(lowPassFilteredPacketsOfTimeDomainData[i])):
        tempUpmixedSamples.append(lowPassFilteredPacketsOfTimeDomainData[i][j] * complexMixingTone[j])
    upmixedSamples.append(tempUpmixedSamples.copy())

#convert from complex to real
upmixedRealSamples = []
for i in range(0,len(upmixedSamples)):
    tempUpmixedRealSamples = []
    for j in range(0,len(upmixedSamples[i])):
        tempUpmixedRealSamples.append(upmixedSamples[i][j].real + upmixedSamples[i][j].imag)
    upmixedRealSamples.append(tempUpmixedRealSamples)

#view spectrum of first packet
xAxis = np.arange(0,len(upmixedSamples[0]),1)
fig, (ax1,ax2) = plt.subplots(nrows=2)
ax1.plot(xAxis, upmixedSamples[0])
ax2.specgram(upmixedSamples[0],64*12,noverlap = 32, Fs=Fs)
fig.show()





#create wave file for each packet
import os
pwd = os.getcwd()
file = pwd + "\\WaveFiles"
for i in range(0,len(upmixedRealSamples)):
    filename = "packet " + str(i) + ".wav"
    wav_file=wave.open(file + "\\" + filename, 'w')
    wav_file.setparams((1, 2, int(48000), len(upmixedRealSamples[i]), "NONE", "not compressed"))
    for j in range(0,len(upmixedRealSamples[i])):
        wav_file.writeframes(struct.pack('h', int(upmixedRealSamples[i][j])))
        
#end for

#transmit packets !NOT A REAL STEP! Just plot it and wait



#combine packets into 1 stream
timeBetweenPackets = 0.001 #seconds
finalDataSet = []
for i in range(0,len(upmixedRealSamples)):
    for j in range(0,len(upmixedRealSamples[i])):
        finalDataSet.append(upmixedRealSamples[i][j])
    for j in range(0,int(timeBetweenPackets//(1/48000))):
        finalDataSet.append(0)
        
#Generate Wave File for overall timeline
wav_file=wave.open(file + "\\overall.wav",'w')
wav_file.setparams((1,2,int(48000),len(finalDataSet), "NONE", "not compressed"))
for i in range(0,len(finalDataSet)):
    wav_file.writeframes(struct.pack('h',int(finalDataSet[i])))
    


##############################################################
#########################  RECEIVER  #########################
##############################################################

#down convert?

#costas loop?

#generate barker code for synchronization
offset = 230
syncMarker = finalDataSet[offset:(lengthOfBarkerSequenceInSamples*12) + offset] #length of samples at baseband * 12 for upsampling

test = np.convolve(syncMarker,finalDataSet)





#cross correlation






