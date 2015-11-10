#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import time
import numpy as np

import config
import pulseaudio as pa

recorder = pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=44100, channels=1)

samplerate = 44100


def record(probeduration):
    #if probeduration == 0:  # I have spent 1 hour with strange bug,
    #    return              # Finally I have found that record(0) had been causing exception
    # with pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=samplerate, channels=1) as recorder:
    #data = recorder.read(int(samplerate * probeduration) * 2)
    data = np.fromstring(recorder.read(int(samplerate * probeduration) * 2), np.int16)
    return data


#def getmax(d):
#    return np.argmax(d)


def quickfft(data):
    d = np.absolute(np.fft.fft(data)).astype(int)
    return d


#def computefreq(data, period):  # TODO
#    return getmax(quickfft(data)) / period


#def pitchanalyze(period):
#    return computefreq(record(period), period)


def gettonepower(tone, data):  # fixed, works independly from bitrate. Only samplerate as outer parameter
    fft = quickfft(data)
    amplitude = fft[int(tone * len(data) / samplerate)]  # = fft[(tone + 0.0) / config.BITRATE]
    return amplitude


def detecttransmission(timeout=15):  # blocking operation, checked
    tryno = timeout * config.BITRATE
    while tryno > 0:
        data = record(1.0/config.BITRATE)  # record len can be modified, it wont affect the code
        lowpower = gettonepower(config.LOW, data)
        highpower = gettonepower(config.HIGH, data)
        if lowpower > config.THRESHOLD or highpower > config.THRESHOLD:
            return True
        tryno -= 1
    return False


def tabdrift(source, padding):  # source is a tab, padding is an offset, samplerate/bitrate is window size, checked
    source = np.array(source)
    x = np.split(source, [padding, padding + samplerate/config.BITRATE])
    return x[1]


def getstronger(source):  # source is record(config.BITRATE), checked
    return config.HIGH if gettonepower(config.HIGH, source) > gettonepower(config.LOW, source) else config.LOW


def synchronize():  # or get record(3 * config.Bitrate), start in the middle and move left, right
    data = record(2 / config.BITRATE)
    windowsize = samplerate / config.BITRATE
    cursor = 0
    offset = windowsize
    # get lower signal
    # move right and check if amplitude has risen
    # if yes, add offset to cursor
    # if no, nop
    signal = getstronger(tabdrift(data, 0))
    signal = config.LOW if signal == config.HIGH else config.HIGH
    for i in range(0, 10):
        offset = int(2 * offset / 3)  # dividing by 2 wasn't working well
        if gettonepower(signal, tabdrift(data, cursor)) < gettonepower(signal, tabdrift(data, cursor + offset)):
            cursor += offset
    # wait cursor samples
    print 'cursor', (cursor + 0.0) / samplerate
    print 'sample', samplerate
    if((cursor + 0.0) / samplerate) > 0:
        x = record((cursor + 0.0) / samplerate)

def getbit():
    return 1 if getstronger(record(1.0/config.BITRATE)) == config.HIGH else 0

def readdata():
    if detecttransmission(45):
        print 'Signal detected'
    else:
        print 'aborting'
        return
    synchronize()
    print 'Synchronized'
    y = getstronger(record(1.0/config.BITRATE))
    while True:
        x = getstronger(record(1.0/config.BITRATE))
        if x == y:
            print 'Error'
            return
        y = x
    print(x)
start = time.time()
readdata()
print time.time() - start

recorder.close()
