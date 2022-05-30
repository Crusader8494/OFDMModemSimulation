#Interleaver Deinterleaver Unit Test
from platform import python_branch
import numpy as np
import matplotlib.pyplot as plt

class InterleaverDeinterleaver:
    
    interleavedData = []
    deinterleavedData = []

    def __init__(self):
        return

    #Interleaver
    def Interleaver(self,data):
        stateOfInterleaverSR0 = 0b0
        stateOfInterleaverSR1 = 0b00
        stateOfInterleaverSR2 = 0b000
        stateOfInterleaverSR3 = 0b0000
        
        tempOutDataReg = 0x00000000
        tempInDataReg = 0b0
        tempData = 0
        stateOfCommutatorSelection = 0

        for i in range(0,len(data)):
            tempOutDataReg = 0
            for j in range(0,32): #run 32 times from MSB to LSB
                tempOutDataReg = (tempOutDataReg << 1) & 0xFFFFFFFF #LOL what am I doing

                #input section
                tempData = data[i]
                tempInDataReg = (tempData >> (31 - j)) & 0b1 #To gain access to the 31st bit, j must be 0. 31 - 0 = 31 left shift => mask bit 0.
                #print("Incomming Bit: " + bin(tempInDataReg))
                if stateOfCommutatorSelection == 0:
                    stateOfInterleaverSR0 =  tempInDataReg #No clock needed
                    stateOfInterleaverSR0 = stateOfInterleaverSR0 & 0b1
                    #print("SR0: " + bin(stateOfInterleaverSR0))
                elif stateOfCommutatorSelection == 1:
                    stateOfInterleaverSR1 = stateOfInterleaverSR1 + tempInDataReg
                    stateOfInterleaverSR1 = (stateOfInterleaverSR1 << 1) & 0b11   #Clock Pulse
                    #print("SR1: " + bin(stateOfInterleaverSR1))
                elif stateOfCommutatorSelection == 2:
                    stateOfInterleaverSR2 = stateOfInterleaverSR2 + tempInDataReg
                    stateOfInterleaverSR2 = (stateOfInterleaverSR2 << 1) & 0b111  #Clock Pulse
                    #print("SR2: " + bin(stateOfInterleaverSR2))
                elif stateOfCommutatorSelection == 3:
                    stateOfInterleaverSR3 = stateOfInterleaverSR3 + tempInDataReg
                    stateOfInterleaverSR3 = (stateOfInterleaverSR3 << 1) & 0b1111 #Clock Pulse
                    #print("SR3: " + bin(stateOfInterleaverSR3))
                else:
                    print("\n!ERROR IN INTERLEAVER INPUT!\n")
                

                #output section
                if stateOfCommutatorSelection == 0:
                    tempOutDataReg = tempOutDataReg + (0b1 & stateOfInterleaverSR0)
                    stateOfCommutatorSelection = stateOfCommutatorSelection + 1
                elif stateOfCommutatorSelection == 1:
                    tempOutDataReg = tempOutDataReg + ((0b10 & stateOfInterleaverSR1) >> 1)
                    stateOfCommutatorSelection = stateOfCommutatorSelection + 1
                elif stateOfCommutatorSelection == 2:
                    tempOutDataReg = tempOutDataReg + ((0b100 & stateOfInterleaverSR2) >> 2)
                    stateOfCommutatorSelection = stateOfCommutatorSelection + 1
                elif stateOfCommutatorSelection == 3:
                    tempOutDataReg = tempOutDataReg + ((0b1000 & stateOfInterleaverSR3) >> 3)
                    stateOfCommutatorSelection = 0
                else:
                    print("!ERROR IN INTERLEAVER OUTPUT!")
                
                #tempOutDataReg = (tempOutDataReg << 1) & 0xFFFFFFFF #LOL what am I doing
            self.interleavedData.append(tempOutDataReg)

        return self.interleavedData
    
    def deinterleaver(self,data):
        stateOfDeinterleaverSR0 = 0b0000
        stateOfDeinterleaverSR1 = 0b000
        stateOfDeinterleaverSR2 = 0b00
        stateOfDeinterleaverSR3 = 0b0
        
        tempOutDataReg = 0x00000000
        tempInDataReg = 0b0
        tempData = 0

        stateOfCommutatorSelection = 0

        for i in range(0,len(data)):
            tempOutDataReg = 0
            for j in range(0,32): #run 32 times from MSB to LSB
                tempOutDataReg = (tempOutDataReg << 1) & 0xFFFFFFFF #LOL what am I doing

                #input section
                tempData = data[i]
                tempInDataReg = (tempData >> (31 - j)) & 0b1 #To gain access to the 31st bit, j must be 0. 31 - 0 = 31 left shift => mask bit 0.
                if stateOfCommutatorSelection == 0:
                    stateOfDeinterleaverSR0 = stateOfDeinterleaverSR0 + tempInDataReg #No clock needed
                    stateOfDeinterleaverSR0 = (stateOfDeinterleaverSR0 << 1) & 0b1111   #Clock Pulse
                elif stateOfCommutatorSelection == 1:
                    stateOfDeinterleaverSR1 = stateOfDeinterleaverSR1 + tempInDataReg
                    stateOfDeinterleaverSR1 = (stateOfDeinterleaverSR1 << 1) & 0b111  #Clock Pulse
                elif stateOfCommutatorSelection == 2:
                    stateOfDeinterleaverSR2 = stateOfDeinterleaverSR2 + tempInDataReg
                    stateOfDeinterleaverSR2 = (stateOfDeinterleaverSR2 << 1) & 0b11 #Clock Pulse
                elif stateOfCommutatorSelection == 3:
                    stateOfDeinterleaverSR3 = tempInDataReg
                else:
                    print("\n!ERROR IN INTERLEAVER INPUT!\n")


                #output section
                if stateOfCommutatorSelection == 0:
                    tempOutDataReg = tempOutDataReg + ((0b1000 & stateOfDeinterleaverSR0) >> 3)
                    stateOfCommutatorSelection = stateOfCommutatorSelection + 1
                elif stateOfCommutatorSelection == 1:
                    tempOutDataReg = tempOutDataReg + ((0b100 & stateOfDeinterleaverSR1) >> 2)
                    stateOfCommutatorSelection = stateOfCommutatorSelection + 1
                elif stateOfCommutatorSelection == 2:
                    tempOutDataReg = tempOutDataReg + ((0b10 & stateOfDeinterleaverSR2) >> 1)
                    stateOfCommutatorSelection = stateOfCommutatorSelection + 1
                elif stateOfCommutatorSelection == 3:
                    tempOutDataReg = tempOutDataReg + ((0b1 & stateOfDeinterleaverSR3))
                    stateOfCommutatorSelection = 0
                else:
                    print("!ERROR IN INTERLEAVER OUTPUT!")
                
                #tempOutDataReg = (tempOutDataReg << 1) & 0xFFFFFFFF #LOL what am I doing
            self.deinterleavedData.append(tempOutDataReg)

        return self.deinterleavedData

if __name__ == "__main__":
    from VoiceDataSynthesizer import VoiceDataSynthesizer
    newData = []
    VDS = VoiceDataSynthesizer(0,256,8E3,440,numOfBits=32)
    intDeint = InterleaverDeinterleaver()
    
    newList = []
    for i in range(0,512):
        newList.append(0xAAAAAAAA + i)

    interleavedData = intDeint.Interleaver(newList)
    deinterleavedData = intDeint.deinterleaver(interleavedData)

    newDeinterleavedData = []
    for i in range(0,len(deinterleavedData)): #convert to signed 32 int from unsiged 32 bit int
        if((deinterleavedData[i] >> 31) & 0x1 == 0x1):
            newDeinterleavedData.append(deinterleavedData[i] - 2**32)
        else:
            newDeinterleavedData.append(deinterleavedData[i])

    xAxis = np.arange(0,len(interleavedData),1)
    fig, (ax1) = plt.subplots(nrows=1)
    ax1.plot(xAxis, newList)
    ax1.plot(xAxis, newDeinterleavedData)
    plt.show()

    if VDS.data == newDeinterleavedData:
        print("Test Passed")
    else:
        print("Test Failed")