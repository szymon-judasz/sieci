#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import time
import numpy as np

import config
import pulseaudio as pa

recorder = pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=44100, channels=1)

samplerate = 44100


def record(probeduration):
    nosample = int(samplerate * probeduration) * 2
    # with pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=samplerate, channels=1) as recorder:
    data = recorder.read(nosample)
    data = np.fromstring(data, np.int16)
    return data


def getmax(d):
    return np.argmax(d)


def quickfft(data):
    d = np.absolute(np.fft.fft(data)).astype(int)
    return d


def computefreq(data, period):  # TODO
    return getmax(quickfft(data)) / period


def pitchanalyze(period):
    return computefreq(record(period), period)


def gettonepower(tone, data):
    fft = quickfft(data)
    amplitude = fft[tone * config.BITRATE]
    return amplitude


def detecttransmission(timeout=15):  # blocking operation,
    tryno = timeout / config.BITRATE
    while tryno > 0:
        data = record(config.BITRATE)
        lowpower = gettonepower(config.LOW, data)
        highpower = gettonepower(config.HIGH, data)
        if lowpower > config.THRESHOLD or highpower > config.THRESHOLD:
            break
        tryno -= 1


def tabdrift(source, padding):  # source is a tab, padding is an offset
    source = np.array(source)
    x = np.split(source, [padding, samplerate + padding])
    return x[1]


def getstronger(source):  # source is record(config.BITRATE)
    return config.HIGH if gettonepower(config.HIGH, source) > gettonepower(config.LOW, source) else config.LOW


def synchronize():  # or get record(3 * config.Bitrate), start in the middle and move left, right
    data = record(2 * config.BITRATE)
    windowsize = samplerate
    cursor = 0
    offset = windowsize
    # get lower signal
    # move right and check if amplitude has risen
    # if yes, add offset to cursor
    # if no, nop
    signal = getstronger(tabdrift(data, 0))
    signal = config.LOW if signal == config.HIGH else config.HIGH
    for i in range(0, 5):
        offset = int(2 * offset / 3)  # dividing by 2 wasn't working well
        if gettonepower(signal, tabdrift(data, cursor)) < gettonepower(signal, tabdrift(data, cursor + offset)):
            cursor += offset
    # wait cursor samples
    print cursor
    record(int(cursor / samplerate))


def readdata():
    detecttransmission()
    print 'Signal detected'
    synchronize()
    print 'Synchronized'


start = time.time()
readdata()

print time.time() - start

recorder.close()
