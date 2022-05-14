#Trellis Unit Test
import numpy as np
import matplotlib.pyplot as plt

def getHammingDistance(e):
    return e['hammingDistance']
def getPointer(e):
    return e['pointer']
def getBit(first,second):
    if first == 0 and second == 0:
        return 0
    elif first == 0 and second == 1:
        return 1
    elif first == 1 and second == 2:
        return 0
    elif first == 1 and second == 3:
        return 1
    elif first == 2 and second == 0:
        return 0
    elif first == 2 and second == 1:
        return 1
    elif first == 3 and second == 2:
        return 0
    elif first == 3 and second == 3:
        return 1
    else:
        print("WHAT THE FUCK")
    return 0

class TrellisUnitTest:
    
    trellisStartOfDataSet = 0
    trellisSizeOfDataSet = 0
    
    initialState = 0b000
    stateOfCE = initialState
    stateOfVD = initialState

    originalVoiceData = []
    encodedVoiceData = []
    decodedVoiceData = []

    trellis = []

    def __init__(self,startOfDataSet,sizeOfDataSet,freqOfVoice,fs):
        self.trellisStartOfDataSet = startOfDataSet
        self.trellisSizeOfDataSet = sizeOfDataSet
        self.originalVoiceData = self.CreateData(freqOfVoice, fs)
        self.encodedVoiceData = self.EncodeData(self.originalVoiceData)
        self.ConstructTrellis()
        self.decodedVoiceData = self.DecodeData(self.encodedVoiceData)
        self.compareDataByPlot()
        return
    
    def CreateData(self, freqOfVoiceData, fs):
        data = []
        for i in range(self.trellisStartOfDataSet, self.trellisStartOfDataSet + self.trellisSizeOfDataSet):
            t = i * 1/fs
            data.append((int(np.cos(2*np.pi*freqOfVoiceData*t)*((2**8)-1))))
        return data

    def EncodeData(self, data):
        newData = []
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
                self.stateOfCE = (self.stateOfCE << 1)  #Clock Pulse
                self.stateOfCE = self.stateOfCE + currentBit #Clock Pulse
                self.stateOfCE = self.stateOfCE & 0b111 #Clock Pulse
                #print("The State of CE After Shift is: " + str(bin(stateOfCE)))

                #determine A and B
                a = ((self.stateOfCE & 0b001) + (self.stateOfCE & 0b010) + (self.stateOfCE & 0b100)) & 0b001
                #print("The Result of a is: " + str(bin(a)))
                b = ((self.stateOfCE & 0b001) + (self.stateOfCE & 0b010)) & 0b001
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
        return newData

    def ConstructTrellis(self):
        forwardTraversalLUT = [[0,1],[2,3],[0,1],[2,3]]
        for i in range(0,4):
            trellisStructure = []
            trellisStructure.clear()
            trellisStructure = [[i]]
            while(1):#build trellis
                #set deadman switch flag
                loopEnd = True
                for j in range(0,len(trellisStructure)):
                    if len(trellisStructure[j]) < 17:
                        #gain initial state
                        tempCopyOfPathOne = []
                        tempCopyOfPathOne = trellisStructure[j].copy()
                        tempCopyOfPathTwo = []
                        tempCopyOfPathTwo = tempCopyOfPathOne.copy()
                        #divrege with 2 copies
                        tempCopyOfPathOne.append(forwardTraversalLUT[tempCopyOfPathOne[len(trellisStructure[j]) - 1]][0])
                        tempCopyOfPathTwo.append(forwardTraversalLUT[tempCopyOfPathTwo[len(trellisStructure[j]) - 1]][1])
                        #remove original 
                        trellisStructure.pop(j)
                        #rewrite copies to master list
                        trellisStructure.append(tempCopyOfPathOne)
                        trellisStructure.append(tempCopyOfPathTwo)
                        #set flag to not end loop
                        loopEnd = False
                if loopEnd == True:
                    self.trellis.append(trellisStructure.copy())
                    break
        return

    def DecodeData(self, encodedData):
        decodedData = []
        previousStartingNode = 0
        for i in range(0, len(encodedData)):
            dataList = []
            tempData = 0
            
            for j in range(0, 16):
                tempData = (tempData & 0xC0000000) >> 30
                dataList.append(tempData)
                tempData = encodedData[i] << (j*2)

            #evaluate and accumulate hamming distance of all paths, then sort
            hammingDistanceList = []
            for j in range(0,len(self.trellis[previousStartingNode])):
                hammingDistance = 0
                for k in range(1,16):
                    hammingDistance += (dataList[k - 1] ^ self.trellis[previousStartingNode][j][k]) & 0x00000003           
                hammingDistanceList.append({'hammingDistance' : hammingDistance, 'pointer' : j}) #unsorted dictionary of distances with original pointers
            #sort list and find answers
            likelyAnswerList = []
            hammingDistanceList.sort(key=getHammingDistance)
            lowestDistance = getHammingDistance(hammingDistanceList[0])
            for i in hammingDistanceList:
                if getHammingDistance(i) == lowestDistance:
                    likelyAnswerList.append(i)
                else:
                    break
            print(likelyAnswerList)

            #extract answer through reverse traverse of the first answer of likelyAnswerList
            doubleByte = 0x0000
            reverseTraverse = self.trellis[previousStartingNode][getPointer(likelyAnswerList[0])].copy()
            for i in range(0,len(reverseTraverse) - 1):
                doubleByte += getBit(reverseTraverse[i],reverseTraverse[i+1])
                doubleByte = (doubleByte << 1) & 0xFFFF
            if((doubleByte >> 15) & 0x1 == 0x1):
                doubleByte -= 2**16
            decodedData.append(doubleByte)
            print(bin(doubleByte))
            print("The Answer Is: " + str(int(bin(doubleByte),2)))

            #set previousNode to last node of first answer
            pointer = getPointer(likelyAnswerList[0])
            previousStartingNode = self.trellis[previousStartingNode][pointer][16]

        return decodedData

    def compareDataByPlot(self):
        plt.plot(np.arange(0,len(self.originalVoiceData),1), self.originalVoiceData)
        plt.plot(np.arange(0,len(self.decodedVoiceData),1), self.decodedVoiceData)
        plt.show()
        return

test = TrellisUnitTest(0,128,350,8E3)

x = 0