#Interleaver Deinterleaver Unit Test
import numpy as np
import matplotlib.pyplot as plt

from VoiceDataSynthesizer import VoiceDataSynthesizer

class ScramblerDescrambler:

    stateOfLFSR = 0b0000000000000000 #set seed here
    
    scrambledData = []

    def __init__(self):
        self.stateOfLFSR = 0b1000101010111111
        self.scrambledData.clear()
        return

    #Shift LFSR
    #Bit 0 = Bit 15 + Bit 4 + Bit 2 + Bit 1
    def ScramblerShift(self, LFSRState):
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
    def Scramble(self, data):
        for i in range(0, len(data)):
            stateOfLFSR = self.ScramblerShift(self.stateOfLFSR)
            self.scrambledData.append(stateOfLFSR ^ data[i])

if __name__=="__main__":
    VoiceData = VoiceDataSynthesizer(0,2**16,8E3,440)
    Scrambler = ScramblerDescrambler()
    
    Scrambler.Scramble(VoiceData.data)
    AlreadyScrambledData = Scrambler.scrambledData.copy()

    Descrambler = ScramblerDescrambler()

    Descrambler.Scramble(AlreadyScrambledData)
    AlreadyDescrambledData = Descrambler.scrambledData.copy()

    if VoiceData.data == AlreadyDescrambledData:
        print("SCRAMBLER_DESCRAMBLER UNIT TEST: PASS")
    else:
        print("SCRAMBLER_DESCRAMBLER UNIT TEST: FAIL")
    