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

    #Cap
    if voltageLeft >= (2**15) - 1:
        voltageLeft = (2**15) - 1
    elif voltageLeft <= -2**15:
        voltageLeft = -2**15
    #Cap
    if voltageRight >= (2**15) - 1:
        voltageRight = (2**15) - 1
    elif voltageRight <= -2**15:
        voltageRight = -2**15

    debugX.append(time)
    debugYLeft.append(voltageLeft)
    debugYRight.append(voltageRight)

rawDataPackets = []
#packetize data // Assume 64 point IFFT // We will map two 16 bit audio samples to 1 OFDM frame (left and right stereo)
for i in range(0,len(voltageLeft)):
    rawDataPackets.append([voltageLeft[i],voltageRight[i]].copy())

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
    mappedData = []
    startingMaskLeft = 0x80000000
    startingMaskRight = 0x80000000
    for j in range(0,64):
        jPrime = j - 31 #nice
        mappedData.append(np.complex(1,1)) #? Hard Coded Pilot Tone in bin 0
        if (jPrime <= -17):
            mappedData.append(np.complex(0,0)) #Hard Coded off
        elif ((jPrime >= -16) & (jPrime <= -1)):
            if ((startingMaskLeft & rawDataPackets[i][0]) == startingMaskLeft): #if it equals 1, then make it 1
                mappedData.append(np.complex(1,1))
            else:
                mappedData.append(np.complex(-1,-1)) #else, its 0 and perform phase flip
            startingMaskLeft = startingMaskLeft >> 1 #right shift once to shift mask for next operation
        elif ((jPrime >= 1) & (jPrime <= 16)):
            if ((startingMaskRight & rawDataPackets[i][1]) == startingMaskRight): #if it equals 1, then make it 1
                mappedData.append(np.complex(1,1))
            else:
                mappedData.append(np.complex(-1,-1)) #else, its 0 and perform phase flip
            startingMaskRight = startingMaskRight >> 1 #right shift once to shift mask for next operation
        elif (jPrime >= 17):
            mappedData.append(np.complex(0,0)) #Hard Coded off
        else:
            raise Exception("what")
    finalMappedData.append(mappedData.copy())

#for i in number of packets
    #create sync marker

    #append time domain data from IFFT

    #mix up and upsample to audio data rates (48000 samples per second)

    #add packet to packet buffer

#end for

#transmit packets !NOT A REAL STEP! Just plot it and wait



