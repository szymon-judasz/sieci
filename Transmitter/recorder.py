#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import sys
import wave
import time
import numpy as np
import config
import pulseaudio as pa

recorder = pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=44100, channels=1)


def record(probeduration):
    samplerate = 44100
    nosample = int(samplerate * probeduration)
    # with pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=samplerate, channels=1) as recorder:
    data = recorder.read(nosample * 2)
    return data


def getmax(d):
    return np.argmax(d)


def generaterawdata(freq, amplitude, time):
    tab = (np.sin(freq / 44100.0 * 2 * np.pi * np.array(range(0, int(44100 * time)))) * amplitude).astype(np.int16)
    return tab


def quickfft(data):
    d = np.absolute(np.fft.fft((np.fromstring(data, np.int16)))).astype(int)
    return d


def computefreq(data, time):
    return getmax(quickfft(data)) / time


def pitchanalyze(time):
    return computefreq(record(time), time)


def getTonePower(tone, data):
    fft = quickfft(data)
    amplitude = fft[tone * config.BITRATE]
    return amplitude


def detectTranssmission(timeout=15):  # blocking operation,
    tryNo = timeout / config.BITRATE
    while tryNo > 0:
        data = record(config.BITRATE)
        lowpower = getTonePower(config.LOW, data)
        highpower = getTonePower(config.HIGH, data)
        if lowpower > config.THRESHOLD or highpower > config.THRESHOLD:
            break
        tryNo -= 1

def tabdrift(source, nosamples):
    source = np.array(source)
    #x = source.

def synchronize(data):
    x = 1


def readData():
    detectTranssmission()
    print 'Signal detected'
    oversample = record(2*config.BITRATE)

# detectTranssmission()
start = time.time()
record(120)
print time.time() - start
recorder.close()
