#Channel Model Simulation
import numpy as np

class ChannelSimulation:

    txAmplitude = 0

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

    def __init__(self, Amp):
        self.txAmplitude = Amp
        return

    def Mapper(self, data):
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
                binList.append(((temp16Bit & 0b1000000000000000) >> 15) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0100000000000000) >> 14) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0010000000000000) >> 13) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0001000000000000) >> 12) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000100000000000) >> 11) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000010000000000) >> 10) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000001000000000) >> 9) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000000100000000) >> 8) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000000010000000) >> 7) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000000001000000) >> 6) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000000000100000) >> 5) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000000000010000) >> 4) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000000000001000) >> 3) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000000000000100) >> 2) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000000000000010) >> 1) * self.txAmplitude)
                binList.append(((temp16Bit & 0b0000000000000001) >> 0) * self.txAmplitude)

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

        return np.array(samplesInTimeWithCP)

    def upSample(self,data): 
        #upsampling from 8kHz to 48 kHz (add 5 0+0j samples every real sample), then run through a filter
        #Filter Params: 48 kHz sampling rate, 4kHz passband, 1kHz transition band

        #Kaiser Window
        newData = []
        for i in range (0, len(data)):
            newData.append(data[i])
            for j in range (0,5):
                newData.append(complex(0,0))
        
        filteredData = np.convolve(newData,self.h)

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

    def downConvertandFilter(self, data, freq):
        result = []
        b = []

        for i in range(0,len(data)):
            t = i * (1/48E3)
            b.append(complex(np.cos(2*np.pi*freq*t),np.sin(2*np.pi*freq*t)))
            result.append(complex((data[i].real * b[i].real) + (data[i].imag * b[i].imag),(data[i].real * b[i].imag) - (b[i].real * data[i].imag)))

        #upsampling from 8kHz to 48 kHz (add 5 0+0j samples every real sample), then run through a filter
        #Filter Params: 48 kHz sampling rate, 4kHz passband, 1kHz transition band

        #Kaiser Window
        
        filteredData = np.convolve(result,self.h)

        return filteredData

    def decimate(data):
        newData = []

        for i in range(0, len(data)):
            if i % 6 == 1:
                newData.append(data[i])

        return newData

    def filterdown(self, data):
        #upsampling from 8kHz to 48 kHz (add 5 0+0j samples every real sample), then run through a filter
        #Filter Params: 48 kHz sampling rate, 4kHz passband, 1kHz transition band

        #Kaiser Window
        
        filteredData = np.convolve(data,self.h)

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