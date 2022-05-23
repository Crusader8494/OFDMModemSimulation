import numpy as np
import matplotlib.pyplot as plt

from VoiceDataSynthesizer import VoiceDataSynthesizer
from ScramblerDescramblerUnitTest import ScramblerDescrambler
from ConvolutionalEncoderViterbiDecoderUnitTest import ConvolutionalEncoderViterbiDecoderUnitTest
from InterleaverDeinterleaverUnitTest import InterleaverDeinterleaver
from ChannelSimulation import ChannelSimulation


#Create Voice Data
#Stable Sine for now
vds = VoiceDataSynthesizer(0,128,8E3,440.0)
print(vds.data)

#Scramble Voice Data
scrambler = ScramblerDescrambler()
scrambler.Scramble(vds.data)
print(scrambler.scrambledData)

#Encode Scrambled Voice Data
ce = ConvolutionalEncoderViterbiDecoderUnitTest()
ce.EncodeData(scrambler.scrambledData)
print(ce.encodedVoiceData)

#Interleave Encoded Scrambled Data
inter = InterleaverDeinterleaver()
inter.Interleaver(ce.encodedVoiceData)
print(inter.interleavedData)