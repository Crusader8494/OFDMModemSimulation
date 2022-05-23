#Interleaver Deinterleaver Unit Test
import numpy as np
import matplotlib.pyplot as plt

class VoiceDataSynthesizer:

    startOfDataSet = 0 #Samples
    sizeOfDataSet = 0 #Samples 
    voiceFs = 0
    freqOfVoiceData = 0.0 #Hz

    data = []

    def __init__(self, startofDataSet, sizeOfDataSet, voiceFs, freqOfVoiceData):
        #CreateData Parameters
        self.startOfDataSet = startofDataSet #Samples
        self.sizeOfDataSet = sizeOfDataSet #Samples 
        self.voiceFs = voiceFs
        self.freqOfVoiceData = freqOfVoiceData #Hz
        self.CreateData()

    #Create Data Set to Transmit
    def CreateData(self):
        self.data.clear()
        for i in range(self.startOfDataSet, self.startOfDataSet + self.sizeOfDataSet):
            t = i * 1/self.voiceFs
            self.data.append((int(np.cos(2*np.pi*self.freqOfVoiceData*t)*((2**8)-1))))