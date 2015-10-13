#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import sys
import wave
import numpy as np

import pulseaudio as pa


def record(probeduration):
    samplerate = 44100
    nosample = int(samplerate * probeduration)
    with pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate = samplerate, channels=1) as recorder:
        data = recorder.read(nosample * 2)
#        d = np.absolute(np.fft.fft((np.fromstring(data, np.int16)))).astype(int)
#        print(getmax(d))
        return data
    
def getmax(d):
    return np.argmax(d)

def generaterawdata(freq, amplitude, time):
    tab = (np.sin(freq / 44100.0 * 2 * np.pi * np.array(range(0,int(44100*time))))*amplitude).astype(np.int16)
    return tab

def quickfft(data):
    d = np.absolute(np.fft.fft((np.fromstring(data, np.int16)))).astype(int)
    return d

def computefreq(data, time):
    return getmax(quickfft(data))/time

def pitchanalyze(time):
    return computefreq(record(time),time)
