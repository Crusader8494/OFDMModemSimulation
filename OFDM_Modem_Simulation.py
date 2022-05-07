#This will be my second go at OFDM
#There will be 16 carriers operating around 12 kHz for the final output

import numpy as np
import matplotlib.pyplot as plt

#Global Parameters
fsForIFFT = 8E3

logEnable = 0

txAmplitude = complex(32,0)

#CreateData Parameters
startOfDataSet = 1600 #Samples
sizeOfDataSet = 64 #Samples 
voiceFs = 8E3
freqOfVoiceData = 443.3 #Hz

#LFSR Parameters
stateOfLFSR = 0b1000101010111111 #set seed here

#Convolutional Encoder Parameters
stateOfCE = 0b000 #initial seed here

h = [
    0.000000000000000000,
    0.000000000000000000,
    0.003634206441754587,
    0.020586560598243708,
    0.061496314232917321,
    0.124207807126850853,
    0.184890257806065827,
    0.210369707588335092,
    0.184890257806065883,
    0.124207807126850880,
    0.061496314232917369,
    0.020586560598243750,
    0.003634206441754590,
    0.000000000000000000,
    0.000000000000000000,
]

h2 = [
    0.000000000000000000,
    0.000000000000000000,
    -0.000011630407605336,
    -0.000016685876162815,
    0.000030714762043070,
    0.000080677137832956,
    0.000000000000000000,
    -0.000172259750367663,
    -0.000145716933132334,
    0.000193698589739695,
    0.000407178976551273,
    -0.000000000000000001,
    -0.000652330200285278,
    -0.000499944562009187,
    0.000613150407171977,
    0.001205088560750828,
    -0.000000000000000002,
    -0.001734906421864614,
    -0.001272953023212590,
    0.001501963522563159,
    0.002851427247674092,
    -0.000000000000000004,
    -0.003867678382179018,
    -0.002765788759986591,
    0.003188024725914361,
    0.005925579956551042,
    -0.000000000000000007,
    -0.007752197536804714,
    -0.005460989694228917,
    0.006213796521650214,
    0.011426132137987179,
    -0.000000000000000010,
    -0.014737544197304983,
    -0.010351779338073271,
    0.011784290468445067,
    0.021765669641354731,
    -0.000000000000000013,
    -0.028768617695195800,
    -0.020674619573705581,
    0.024324730749154904,
    0.047085117073133585,
    -0.000000000000000015,
    -0.073397829386347938,
    -0.061300551078186820,
    0.092835555199572942,
    0.302151635285898779,
    0.399999183705328054,
    0.302151635285898779,
    0.092835555199572956,
    -0.061300551078186820,
    -0.073397829386347938,
    -0.000000000000000015,
    0.047085117073133578,
    0.024324730749154904,
    -0.020674619573705588,
    -0.028768617695195797,
    -0.000000000000000013,
    0.021765669641354735,
    0.011784290468445067,
    -0.010351779338073273,
    -0.014737544197304983,
    -0.000000000000000010,
    0.011426132137987190,
    0.006213796521650211,
    -0.005460989694228918,
    -0.007752197536804716,
    -0.000000000000000007,
    0.005925579956551044,
    0.003188024725914359,
    -0.002765788759986593,
    -0.003867678382179019,
    -0.000000000000000004,
    0.002851427247674094,
    0.001501963522563160,
    -0.001272953023212590,
    -0.001734906421864614,
    -0.000000000000000002,
    0.001205088560750829,
    0.000613150407171977,
    -0.000499944562009187,
    -0.000652330200285277,
    -0.000000000000000001,
    0.000407178976551273,
    0.000193698589739695,
    -0.000145716933132334,
    -0.000172259750367663,
    0.000000000000000000,
    0.000080677137832956,
    0.000030714762043070,
    -0.000016685876162815,
    -0.000011630407605336,
    0.000000000000000000,
    0.000000000000000000]
h1 = [
    0.000003516313066004,
    0.000000000000000000,
    -0.000005626568507648,
    -0.000011935798753968,
    -0.000016620139971312,
    -0.000017138764253919,
    -0.000011658368490262,
    0.000000000000000000,
    0.000015771490809181,
    0.000031434143079255,
    0.000041516479189633,
    0.000040903584117308,
    0.000026736480107001,
    0.000000000000000000,
    -0.000033833409723097,
    -0.000065547292697069,
    -0.000084371634106615,
    -0.000081195525478028,
    -0.000051940340042547,
    0.000000000000000000,
    0.000063253702546053,
    0.000120458499530723,
    0.000152585949570021,
    0.000144652097370140,
    0.000091235826068460,
    0.000000000000000000,
    -0.000108270799352941,
    -0.000203749448036117,
    -0.000255195230137931,
    -0.000239345201728175,
    -0.000149427516204209,
    0.000000000000000002,
    0.000173983670359875,
    0.000324512204387667,
    0.000403003295533186,
    0.000374899741534510,
    0.000232229997921378,
    -0.000000000000000001,
    -0.000266430951857418,
    -0.000493495138959344,
    -0.000608762564540477,
    -0.000562662224210343,
    -0.000346373360009732,
    -0.000000000000000001,
    0.000392716453081169,
    0.000723341280120552,
    0.000887476647275092,
    0.000815989499557066,
    0.000499787189958568,
    -0.000000000000000002,
    -0.000561234134713910,
    -0.001029019725730187,
    -0.001256952117432201,
    -0.001150778201123652,
    -0.000701939301964724,
    0.000000000000000007,
    0.000782084082521598,
    0.001428623992248344,
    0.001738819881199008,
    0.001586444652451181,
    0.000964462422865203,
    -0.000000000000000002,
    -0.001067841304019511,
    -0.001944846845520484,
    -0.002360421448622634,
    -0.002147734440895997,
    -0.001302311729888382,
    0.000000000000000003,
    0.001434977847865747,
    0.002607712089163846,
    0.003158309048262063,
    0.002868087787575393,
    0.001735923520109984,
    -0.000000000000000004,
    -0.001906533735676951,
    -0.003459727712318664,
    -0.004184880889625475,
    -0.003796054866488980,
    -0.002295355667559899,
    0.000000000000000004,
    0.002517313462445680,
    0.004565993451861406,
    0.005521510947697017,
    0.005008111813898382,
    0.003028644373498169,
    -0.000000000000000005,
    -0.003324616325539702,
    -0.006035337255195691,
    -0.007306377997769329,
    -0.006636217948036958,
    -0.004020050177365722,
    0.000000000000000005,
    0.004432465837868627,
    0.008068929525381402,
    0.009799739199600539,
    0.008933812691298412,
    0.005434735066801748,
    -0.000000000000000006,
    -0.006053903204726415,
    -0.011088671945112968,
    -0.013561336115385113,
    -0.012460786933720569,
    -0.007648179517199455,
    0.000000000000000006,
    0.008705247710662990,
    0.016154510895018775,
    0.020053580899052938,
    0.018744048502887915,
    0.011733923877030024,
    -0.000000000000000006,
    -0.014035969392875727,
    -0.026883722770503594,
    -0.034656937489231709,
    -0.033910007366119703,
    -0.022459223507597263,
    0.000000000000000006,
    0.031632827104199249,
    0.068641829193861956,
    0.105866642035830502,
    0.137697274158993965,
    0.159118713455543070,
    0.166670492544289589,
    0.159118713455543070,
    0.137697274158993965,
    0.105866642035830502,
    0.068641829193861956,
    0.031632827104199249,
    0.000000000000000006,
    -0.022459223507597263,
    -0.033910007366119703,
    -0.034656937489231709,
    -0.026883722770503594,
    -0.014035969392875727,
    -0.000000000000000006,
    0.011733923877030024,
    0.018744048502887915,
    0.020053580899052938,
    0.016154510895018775,
    0.008705247710662990,
    0.000000000000000006,
    -0.007648179517199455,
    -0.012460786933720569,
    -0.013561336115385113,
    -0.011088671945112968,
    -0.006053903204726415,
    -0.000000000000000006,
    0.005434735066801748,
    0.008933812691298412,
    0.009799739199600539,
    0.008068929525381402,
    0.004432465837868627,
    0.000000000000000005,
    -0.004020050177365722,
    -0.006636217948036958,
    -0.007306377997769329,
    -0.006035337255195691,
    -0.003324616325539702,
    -0.000000000000000005,
    0.003028644373498169,
    0.005008111813898382,
    0.005521510947697017,
    0.004565993451861406,
    0.002517313462445680,
    0.000000000000000004,
    -0.002295355667559899,
    -0.003796054866488980,
    -0.004184880889625475,
    -0.003459727712318664,
    -0.001906533735676951,
    -0.000000000000000004,
    0.001735923520109984,
    0.002868087787575393,
    0.003158309048262063,
    0.002607712089163848,
    0.001434977847865747,
    0.000000000000000003,
    -0.001302311729888382,
    -0.002147734440895997,
    -0.002360421448622634,
    -0.001944846845520484,
    -0.001067841304019512,
    -0.000000000000000002,
    0.000964462422865202,
    0.001586444652451181,
    0.001738819881199008,
    0.001428623992248344,
    0.000782084082521598,
    0.000000000000000007,
    -0.000701939301964724,
    -0.001150778201123653,
    -0.001256952117432201,
    -0.001029019725730187,
    -0.000561234134713910,
    -0.000000000000000002,
    0.000499787189958568,
    0.000815989499557066,
    0.000887476647275092,
    0.000723341280120552,
    0.000392716453081168,
    -0.000000000000000001,
    -0.000346373360009732,
    -0.000562662224210343,
    -0.000608762564540477,
    -0.000493495138959344,
    -0.000266430951857418,
    -0.000000000000000001,
    0.000232229997921378,
    0.000374899741534510,
    0.000403003295533186,
    0.000324512204387667,
    0.000173983670359875,
    0.000000000000000002,
    -0.000149427516204209,
    -0.000239345201728175,
    -0.000255195230137931,
    -0.000203749448036117,
    -0.000108270799352941,
    0.000000000000000000,
    0.000091235826068460,
    0.000144652097370140,
    0.000152585949570021,
    0.000120458499530723,
    0.000063253702546053,
    0.000000000000000000,
    -0.000051940340042547,
    -0.000081195525478028,
    -0.000084371634106615,
    -0.000065547292697069,
    -0.000033833409723097,
    0.000000000000000000,
    0.000026736480107001,
    0.000040903584117308,
    0.000041516479189633,
    0.000031434143079255,
    0.000015771490809181,
    0.000000000000000000,
    -0.000011658368490262,
    -0.000017138764253919,
    -0.000016620139971312,
    -0.000011935798753968,
    -0.000005626568507648,
    0.000000000000000000,
    0.000003516313066004]


#Create Data Set to Transmit
def CreateData(freqOfVoiceData, fs):
    data = []
    for i in range(startOfDataSet, startOfDataSet + sizeOfDataSet):
        t = i * 1/fs
        data.append((int(np.cos(2*np.pi*freqOfVoiceData*t)*((2**8)-1))))
    return data

#Shift LFSR
#Bit 0 = Bit 15 + Bit 4 + Bit 2 + Bit 1
def ScramblerShift(LFSRState):
    #Take state of LFSR and mask in values for the adder coming up
    bit15 = (0b1000000000000000 & LFSRState) >> 15
    bit4  = (0b0000000000010000 & LFSRState) >> 4
    bit2  = (0b0000000000000100 & LFSRState) >> 2
    bit1  = (0b0000000000000010 & LFSRState) >> 1

    #Shift
    LFSRState = LFSRState << 1
    #Mask post shift
    LFSRState = LFSRState & 0x0000FFFF

    #Sum bits without overflow protection
    sum = bit15 + bit4 + bit2 + bit1

    #Mask the result of the addition
    maskedSum = sum & 0b0000000000000001

    #Add Result
    LFSRState = LFSRState + maskedSum
    
    return LFSRState

#Test for LFSR
#for i in range(0,32767):
#    stateOfLFSR = ScramblerShift(stateOfLFSR)
#    print(bin(stateOfLFSR))

#Scramble Data
def Scramble(data, LFSRStateIs):
    scrambledData = []
    for i in range(0, len(data)):
        LFSRStateIs = ScramblerShift(LFSRStateIs)
        scrambledData.append(LFSRStateIs ^ data[i])
    if logEnable == 1:
        print("\nScrambed Data: " + str(scrambledData) + "\n")
    return scrambledData

#Channel Coder
#Input: 0x0000
#Output: 0x00000000
def ChannelCoder(data, stateOfCE, encodeDecode):
    newData = []
    
    if encodeDecode == True:
        for i in range(0, len(data)):
            QWordToBuild = 0x00000000
            tempDWord = data[i]
            #print("The Current DWord is: " + str(bin(tempDWord)))

            for j in range(0, 16):
                currentBit = tempDWord & 0b1000000000000000
                currentBit = currentBit >> 15
                currentBit = currentBit & 0b0000000000000001
                
                #print("The Current Bit is: " + str(bin(currentBit)))
                
                #print("The State of CE Before Shift is: " + str(bin(stateOfCE)))
                stateOfCE = (stateOfCE << 1)  #Clock Pulse
                stateOfCE = stateOfCE + currentBit #Clock Pulse
                stateOfCE = stateOfCE & 0b111 #Clock Pulse
                #print("The State of CE After Shift is: " + str(bin(stateOfCE)))

                #determine A and B
                a = ((stateOfCE & 0b001) + (stateOfCE & 0b010) + (stateOfCE & 0b100)) & 0b001
                #print("The Result of a is: " + str(bin(a)))
                b = ((stateOfCE & 0b001) + (stateOfCE & 0b010)) & 0b001
                #print("The Result of b is: " + str(bin(b)))
                ###### FAKE NEWS GARBAGE ##### tempDoubleBit = a + b

                QWordToBuild = QWordToBuild + a
                QWordToBuild = QWordToBuild << 1
                QWordToBuild = QWordToBuild + b
                QWordToBuild = QWordToBuild << 1
                QWordToBuild = QWordToBuild & 0xFFFFFFFF

                #print("The Current QWord is: " + str(bin(QWordToBuild)))
                tempDWord = tempDWord << 1
                tempDWord = tempDWord  & 0xFFFF
                #print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            newData.append(QWordToBuild)
        if logEnable == 1:
            print("\nConvolutional Encoded Samples: " + str(newData) + "\n")
    else:# decode (viterbi)
        #model:
        #0 -> 0 or 1
        #1 -> 2 or 3
        #2 -> 0 or 1
        #3 -> 2 or 3
        #trellis should be represented as a list (multiple iterations of the trellis) of...
        #lists (each row of the trellis) of lists (multiple paths to those rows if they exist) of...
        #lists (previous node and hamming distance)
        trellis = []
        #trellis = [[[tuple(previousNode, hammingDistance)]]]
        trellisColumn = []
        #trellisColumn = [[tuple(previousNode, hammingDistance)]]
        trellisColumnNode = []
        #trellisColumnNode = [tuple(previousNode, hammingDistance)]
        trellisColumnNodeInformation = tuple(-1,0)
        #trellisColumnNodeInformation = tuple(previousNode, hammingDistance)
        previousNode = 0 #0,1,2 or 3
        hammingDistance = 0
        for i in range(0, len(data)):
            dataList = []
            tempData = 0
            for j in range(0, 16):
                tempData = (tempData & 0xC0000000) >> 30
                dataList.append(tempData)
                tempData = data[i] << (j*2)
            for j in range(0, 16):
                for k in range(0, 4):
                    #create nodes and branch
                    if len(trellis) == 0:
                        hammingDistance = (dataList[j] ^ 0b00) & 0x00000003
                        trellisColumnNodeInformation = tuple(-1,hammingDistance) #-1 denotes root node
                        trellisColumnNodeInformation.append(trellisColumnNodeInformation)
                        break #exit due to initial state
                    elif len(trellis) == 1:
                        
                    else:

                trellisColumnNode.append(trellisColumnNodeInformation)
                trellisColumn.append(trellisColumnNode)
                trellis.append(trellisColumn)
                        #destroy nodes / find lowest hamming distance at each node and elimate all other paths at each node
                

    return newData


#Interleaver
def Interleaver(data):
    stateOfInterleaverSR0 = 0b0
    stateOfInterleaverSR1 = 0b00
    stateOfInterleaverSR2 = 0b000
    stateOfInterleaverSR3 = 0b0000
    
    tempOutDataReg = 0x00000000
    tempInDataReg = 0b0
    tempData = 0
    dataOut = []
    stateOfCommutatorSelection = 0

    for i in range(0,len(data)):
        tempOutDataReg = 0
        for j in range(0,32): #run 32 times from MSB to LSB, j is not used?
            
            #input section
            tempData = data[i]
            tempInDataReg = (tempData >> (31 - j)) & 0b1 #To gain access to the 31st bit, j must be 0. 31 - 0 = 31 left shift => mask bit 0.
            if stateOfCommutatorSelection == 0:
                stateOfInterleaverSR0 = stateOfInterleaverSR0 + tempInDataReg #No clock needed
            elif stateOfCommutatorSelection == 1:
                stateOfInterleaverSR1 = stateOfInterleaverSR1 + tempInDataReg
            elif stateOfCommutatorSelection == 2:
                stateOfInterleaverSR2 = stateOfInterleaverSR2 + tempInDataReg
            elif stateOfCommutatorSelection == 3:
                stateOfInterleaverSR3 = stateOfInterleaverSR3 + tempInDataReg
            else:
                print("\n!ERROR IN INTERLEAVER INPUT!\n")

            stateOfInterleaverSR1 = (stateOfInterleaverSR1 << 1) & 0b11   #Clock Pulse
            stateOfInterleaverSR2 = (stateOfInterleaverSR2 << 1) & 0b111  #Clock Pulse
            stateOfInterleaverSR3 = (stateOfInterleaverSR3 << 1) & 0b1111 #Clock Pulse

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
            
            tempOutDataReg = (tempOutDataReg << 1) & 0xFFFFFFFF #LOL what am I doing
        dataOut.append(tempOutDataReg)
    if logEnable == 0:
        print("Interleaved Data: " + str(dataOut) + "\n")
    return dataOut

#Map to OFDM Scheme and go to Time Domain
#do not confuse with QAM Mapper
def Mapper(data):
    samplesGroupedByIFFTFrameInTime = []
    temp16Bit = 0x0000

    for i in range(0,len(data)):

        for j in range(0,2):
            if j == 0: #High Double Byte
                temp16Bit = (data[i] & 0xFFFF0000) >> 16
            elif j == 1: #Low Double Byte
                temp16Bit = (data[i] & 0x0000FFFF) >> 0
            else:
                print("ERROR IN MAPPER")
        
            binList = []
            binList.append(((temp16Bit & 0b1000000000000000) >> 15) * txAmplitude)
            binList.append(((temp16Bit & 0b0100000000000000) >> 14) * txAmplitude)
            binList.append(((temp16Bit & 0b0010000000000000) >> 13) * txAmplitude)
            binList.append(((temp16Bit & 0b0001000000000000) >> 12) * txAmplitude)
            binList.append(((temp16Bit & 0b0000100000000000) >> 11) * txAmplitude)
            binList.append(((temp16Bit & 0b0000010000000000) >> 10) * txAmplitude)
            binList.append(((temp16Bit & 0b0000001000000000) >> 9) * txAmplitude)
            binList.append(((temp16Bit & 0b0000000100000000) >> 8) * txAmplitude)
            binList.append(((temp16Bit & 0b0000000010000000) >> 7) * txAmplitude)
            binList.append(((temp16Bit & 0b0000000001000000) >> 6) * txAmplitude)
            binList.append(((temp16Bit & 0b0000000000100000) >> 5) * txAmplitude)
            binList.append(((temp16Bit & 0b0000000000010000) >> 4) * txAmplitude)
            binList.append(((temp16Bit & 0b0000000000001000) >> 3) * txAmplitude)
            binList.append(((temp16Bit & 0b0000000000000100) >> 2) * txAmplitude)
            binList.append(((temp16Bit & 0b0000000000000010) >> 1) * txAmplitude)
            binList.append(((temp16Bit & 0b0000000000000001) >> 0) * txAmplitude)

            if logEnable == 1:
                print("BINLIST: " + str(i) + ": " + str(binList) + "\n")

            samplesGroupedByIFFTFrameInTime.append(np.fft.ifft([binList[7],binList[8],binList[9],binList[10],binList[11],binList[12],binList[13],binList[14],binList[15],binList[0],binList[1],binList[2],binList[3],binList[4],binList[5],binList[6]]))
    

    samplesInTimeWithCP = []

    for i in range(0, len(samplesGroupedByIFFTFrameInTime)):
        for j in range(0,1):
            for k in range(0, 20):
                if k == 0:
                    samplesInTimeWithCP.append(samplesGroupedByIFFTFrameInTime[i][12])
                elif k == 1:
                    samplesInTimeWithCP.append(samplesGroupedByIFFTFrameInTime[i][13])
                elif k == 2:
                    samplesInTimeWithCP.append(samplesGroupedByIFFTFrameInTime[i][14])
                elif k == 3:
                    samplesInTimeWithCP.append(samplesGroupedByIFFTFrameInTime[i][15])
                else:
                    samplesInTimeWithCP.append(samplesGroupedByIFFTFrameInTime[i][k - 4])
        if logEnable == 1:
            print("\nComplex IFFT Output Samples: " + str(samplesInTimeWithCP) + "\n")

    return np.array(samplesInTimeWithCP)

def upSample(data): 
    #upsampling from 8kHz to 48 kHz (add 5 0+0j samples every real sample), then run through a filter
    #Filter Params: 48 kHz sampling rate, 4kHz passband, 1kHz transition band

    #Kaiser Window
    newData = []
    for i in range (0, len(data)):
        newData.append(data[i])
        for j in range (0,5):
            newData.append(complex(0,0))
    
    filteredData = np.convolve(newData,h)
    if logEnable == 1:
        print("\nComplex IFFT Output Samples Filtered: " + str(filteredData) + "\n")

    return np.array(filteredData)

def upConvertandFilter(data, freq):
    result = []
    b = []

    for i in range(0,len(data)):
        t = i * (1/48E3)
        b.append(complex(np.cos(2*np.pi*freq*t),np.sin(2*np.pi*freq*t)))
        result.append(complex((data[i].real * b[i].real) + (data[i].imag * b[i].imag),(data[i].real * b[i].imag) - (b[i].real * data[i].imag)))

    return np.array(result)

def addChannelNoise(data, serverityOfNoise):
    newData = []
    np.random.seed(19680801)

    for i in range(0, len(data)):
        randomVal = np.random.random()
        newSample = data[i] + complex((serverityOfNoise * randomVal),(serverityOfNoise * randomVal))
        #newQ = data[i].imag + (serverityOfNoise * np.random.random()))

        newData.append(newSample)
    #print(newData)
    return np.array(newData)

def downConvertandFilter(data, freq):
    result = []
    b = []

    for i in range(0,len(data)):
        t = i * (1/48E3)
        b.append(complex(np.cos(2*np.pi*freq*t),np.sin(2*np.pi*freq*t)))
        result.append(complex((data[i].real * b[i].real) + (data[i].imag * b[i].imag),(data[i].real * b[i].imag) - (b[i].real * data[i].imag)))

    #upsampling from 8kHz to 48 kHz (add 5 0+0j samples every real sample), then run through a filter
    #Filter Params: 48 kHz sampling rate, 4kHz passband, 1kHz transition band

    #Kaiser Window
    
    filteredData = np.convolve(result,h)
    if logEnable == 1:
        print("\nComplex IFFT Output Samples Filtered: " + str(filteredData) + "\n")

    return filteredData

def decimate(data):
    newData = []

    for i in range(0, len(data)):
        if i % 6 == 1:
            newData.append(data[i])

    return newData

def filterdown(data):
    #upsampling from 8kHz to 48 kHz (add 5 0+0j samples every real sample), then run through a filter
    #Filter Params: 48 kHz sampling rate, 4kHz passband, 1kHz transition band

    #Kaiser Window
    
    filteredData = np.convolve(data,h)
    if logEnable == 1:
        print("\nComplex IFFT Output Samples Filtered: " + str(filteredData) + "\n")

    return filteredData

def receiveSignal(data):
    newData = []
    tempData = []
    offset = 0
    i = 0
    j = 0

    while(i != len(data)):
        for j in range(0, 16):
            if i + j >= len(data):
                break
            else:
                tempData.append(data[i + j])
            if i + 1 >= len(data) - 1:
                break
            else:
                i = i + 1
        
        newData.append(np.fft.fft(tempData))
        tempData.clear()
        if i + 2 >= len(data) - 1:
            break
        else:
            i = i + 4 # Throw out 4 samples for CP

    #print(newData)
    return newData

def convertMagnitudeToData(data,threshold):
    newData = []
    tempData = 0x0000
    tempBit = 0b0
    tempMag = -50 #dBm
    #samplesGroupedByIFFTFrameInTime.append(np.fft.ifft([binList[7],binList[8],binList[9],binList[10],binList[11],
    #binList[12],binList[13],binList[14],binList[15],binList[0],binList[1],binList[2],binList[3],binList[4],binList[5],binList[6]]))
    for i in range(0, len(data)):
        if len(data[i]) != 0:
            for j in range(0,16):
                if j >= 7 and j <= 15:
                    tempMag = data[i][j-7]
                elif j >= 0 and j <= 6:
                    tempMag = data[i][j+9]
                else:
                    print("ERROR IN ConvertMagnitudeToData")
                
                if tempMag >= threshold:
                    tempBit = 0b1
                else:
                    tempBit = 0b0

                tempData = (tempData + (tempBit & 0b1)) & 0xFFFF
                tempData = (tempData << 1) & 0xFFFF
        else:
            tempData = 0x0000
        newData.append(tempData)

    return newData

def deinterleaver(data):
    stateOfDeinterleaverSR0 = 0b0000
    stateOfDeinterleaverSR1 = 0b000
    stateOfDeinterleaverSR2 = 0b00
    stateOfDeinterleaverSR3 = 0b0
    
    tempOutDataReg = 0x00000000
    tempInDataReg = 0b0
    tempData = 0
    dataOut = []
    stateOfCommutatorSelection = 0

    for i in range(0,len(data)):
        tempOutDataReg = 0
        for j in range(0,32): #run 32 times from MSB to LSB, j is not used?
            
            #input section
            tempData = data[i]
            tempInDataReg = (tempData >> (31 - j)) & 0b1 #To gain access to the 31st bit, j must be 0. 31 - 0 = 31 left shift => mask bit 0.
            if stateOfCommutatorSelection == 0:
                stateOfDeinterleaverSR0 = stateOfDeinterleaverSR0 + tempInDataReg #No clock needed
            elif stateOfCommutatorSelection == 1:
                stateOfDeinterleaverSR1 = stateOfDeinterleaverSR1 + tempInDataReg
            elif stateOfCommutatorSelection == 2:
                stateOfDeinterleaverSR2 = stateOfDeinterleaverSR2 + tempInDataReg
            elif stateOfCommutatorSelection == 3:
                stateOfDeinterleaverSR3 = stateOfDeinterleaverSR3 + tempInDataReg
            else:
                print("\n!ERROR IN INTERLEAVER INPUT!\n")

            stateOfDeinterleaverSR0 = (stateOfDeinterleaverSR0 << 1) & 0b1111   #Clock Pulse
            stateOfDeinterleaverSR1 = (stateOfDeinterleaverSR1 << 1) & 0b111  #Clock Pulse
            stateOfDeinterleaverSR2 = (stateOfDeinterleaverSR2 << 1) & 0b11 #Clock Pulse

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
            
            tempOutDataReg = (tempOutDataReg << 1) & 0xFFFFFFFF #LOL what am I doing
        dataOut.append(tempOutDataReg)
    if logEnable == 0:
        print("Interleaved Data: " + str(dataOut) + "\n")
    return dataOut

def convertToMagnitude(data):
    newData = []
    finalData = []

    for i in range(0,len(data)):
        for j in range(0,16):
            if len(data[i]) < 16:
                break
            else:
                newData.append(int(20 * np.log10(np.sqrt((data[i][j].real**2) + (data[i][j].imag**2)))))
        finalData.append(newData.copy())
        newData.clear()

    return finalData



def createSpectrogram(data, fs, nPts, overlap):

    dt = 1/fs
    t = []

    for i in range(0, len(data)):
        t.append(dt * i)

    NFFT = nPts  # the length of the windowing segments
    Fs = fs  # the sampling frequency

    fig, (ax1, ax2) = plt.subplots(nrows=2)
    ax1.plot(t, np.array(data).real)
    ax1.plot(t, np.array(data).imag)
    Pxx, freqs, bins, im = ax2.specgram(data, NFFT=NFFT, mode='magnitude', scale='dB',Fs=Fs, noverlap=overlap)
    #Pxx, freqs, bins, im = ax3.specgram(data, NFFT=NFFT, mode='phase',Fs=Fs, noverlap=0)
    # The `specgram` method returns 4 objects. They are:
    # - Pxx: the periodogram
    # - freqs: the frequency vector
    # - bins: the centers of the time bins
    # - im: the .image.AxesImage instance representing the data in the plot
    plt.show()
    return

def runBIT():
    global stateOfLFSR, stateOfCE
    success = False

    testOrigData = CreateData(350, 8E3)

    #Scramble Test
    testStateOfLFSR = stateOfLFSR
    scrambleTestSuccess = False
    testScrambledData = Scramble(testOrigData, testStateOfLFSR)
    testStateOfLFSR = 0b1000101010111111
    testDescrambledData = Scramble(testScrambledData, testStateOfLFSR)
    print("PreScrambled: " + str(testOrigData))
    print("PostDeScrambled: " + str(testDescrambledData))
    if testOrigData == testDescrambledData:
        scrambleTestSuccess = True
    
    #Encoder Test
    testStateOfCE = stateOfCE
    encoderTestSuccess = False
    testEncodedData = ChannelCoder(testOrigData, testStateOfCE)
    testStateOfCE = stateOfCE


    return
#Main Program

if runBIT() == True:
    print("GREAT SUCCESS")
else:
    print("NO SUCCESS")


originalData = CreateData(freqOfVoiceData, voiceFs)

scrambledData = Scramble(originalData, stateOfLFSR)

convolutionalEncodedData = ChannelCoder(scrambledData, stateOfCE, True)

interleavedData = Interleaver(convolutionalEncodedData)

timeDomainSamples = Mapper(interleavedData)
createSpectrogram(timeDomainSamples, 8E3, 16,0)

upsampledTimeDomainSamples = upSample(timeDomainSamples)
createSpectrogram(upsampledTimeDomainSamples, 48E3, 16*6,0)

upconvertedFilteredTimeDomainSamples = upConvertandFilter(upsampledTimeDomainSamples, 12E3)
createSpectrogram(upconvertedFilteredTimeDomainSamples, 48E3, 16*6,0)

upconvertedFilteredTimeDomainSamplesWithNoise = addChannelNoise(upconvertedFilteredTimeDomainSamples,0.05)

downconvertedTimeDomainSamplesWithNoise = downConvertandFilter(upconvertedFilteredTimeDomainSamplesWithNoise,12E3)
createSpectrogram(downconvertedTimeDomainSamplesWithNoise, 48E3, 16*6,0)

decimatedDownconvertedTimeDomainSamplesWithNoise = decimate(downconvertedTimeDomainSamplesWithNoise)
createSpectrogram(decimatedDownconvertedTimeDomainSamplesWithNoise, 8E3, 16,0)

fftdSignal = receiveSignal(decimatedDownconvertedTimeDomainSamplesWithNoise)

magnitudeBinnedSignal = convertToMagnitude(fftdSignal)
#for i in range(0,len(magnitudeBinnedSignal)):
#    print("Frame " + str(i) + ": ")
#    print(magnitudeBinnedSignal[i])

dataFromMagnitude = convertMagnitudeToData(magnitudeBinnedSignal,10)
#for i in range(0,len(dataFromMagnitude)):
#    print("Frame " + str(i) + ": ")
#    print(dataFromMagnitude[i])

deinterleavedData = deinterleaver(dataFromMagnitude)

#plot Interleaved vs. Deinterleaved Data
xAxis = []
lenOfXAxis = 0
y1 = []
y2 = []
if len(interleavedData) < len(deinterleavedData):
    lenOfXAxis = len(interleavedData)
else:
    lenOfXAxis = len(deinterleavedData)
for i in range(0, lenOfXAxis):
    xAxis.append(i)
    y1.append(interleavedData[i])
    y2.append(deinterleavedData[i])
fig, (ax1) = plt.subplots(nrows=1)
ax1.plot(xAxis, y1)
ax1.plot(xAxis, y2)
plt.show()