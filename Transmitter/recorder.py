#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import time
import numpy as np

import config
import pulseaudio as pa

recorder = pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=44100, channels=1)

samplerate = 44100


def record(probeduration):
    # if probeduration == 0:  # I have spent 1 hour with strange bug,
    #    return              # Finally I have found that record(0) had been causing exception
    # with pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=samplerate, channels=1) as recorder:
    # data = recorder.read(int(samplerate * probeduration) * 2)
    data = np.fromstring(recorder.read(int(samplerate * probeduration) * 2), np.int16)
    return data


# def getmax(d):
#    return np.argmax(d)


def quickfft(data):
    d = np.absolute(np.fft.fft(data)).astype(int)
    return d


# def computefreq(data, period):  # TODO
#    return getmax(quickfft(data)) / period


# def pitchanalyze(period):
#    return computefreq(record(period), period)


def gettonepower(tone, data):  # fixed, works independly from bitrate. Only samplerate as outer parameter
    fft = quickfft(data)
    #amplitude = fft[int(tone * len(data) / samplerate)]  # = fft[(tone + 0.0) / config.BITRATE]  # get max from nearby values
    return np.max(tabdrift(fft, int(tone * len(data) / samplerate) - 3, 6))


def detecttransmission(timeout=15):  # blocking operation, checked
    tryno = timeout * config.BITRATE
    while tryno > 0:
        data = record(1.0 / config.BITRATE)  # record len can be modified, it wont affect the code
        lowpower = gettonepower(config.LOW, data)
        highpower = gettonepower(config.HIGH, data)
        if lowpower > config.THRESHOLD or highpower > config.THRESHOLD:
            return True
        tryno -= 1
    return False


def tabdrift(source, padding, windowsize=samplerate / config.BITRATE):  # source is a tab, padding is an offset in terms of samples, samplerate/bitrate is window size, checked
    source = np.array(source)
    x = np.split(source, [padding, padding + windowsize])
    return x[1]


def getstronger(source):  # source is ie record(config.BITRATE) or any source of different size, checked
    return config.HIGH if gettonepower(config.HIGH, source) > gettonepower(config.LOW, source) else config.LOW


def synchronize():  # or get record(3 * config.Bitrate), start in the middle and move left, right
    data = record(2.0 / config.BITRATE)
    windowsize = samplerate / config.BITRATE
    cursor = 0
    offset = windowsize
    # get lower signal
    # move right and check if amplitude has risen
    # if yes, add offset to cursor
    # if no, nop
    signal = getstronger(tabdrift(data, 0))
    signal = config.LOW if signal == config.HIGH else config.HIGH
    for i in range(0, 4):
        offset = int(1 * offset / 2)  # dividing by 2 wasn't working well
        if gettonepower(signal, tabdrift(data, cursor)) < gettonepower(signal, tabdrift(data, cursor + offset)):
            cursor += offset
    # wait cursor samples
    print 'cursor', (cursor + 0.0) / samplerate
    print 'sample', samplerate
    if ((cursor + 0.0) / samplerate) > 0:
        x = record((cursor + 0.0) / samplerate)


def getadjust(data):
    signal = getstronger(data)
    adjust = 0
    original = gettonepower(signal, data)
    begining = gettonepower(signal, tabdrift(data, 0, 0.9 * samplerate / config.BITRATE))
    ending = gettonepower(signal, tabdrift(data, 0.1 * samplerate / config.BITRATE, 0.9 * samplerate / config.BITRATE))
#    print 'original = ', original
#    print 'begini = ', begining
#    print 'ending = ', ending
    if original < begining:
#        print('--------------------------------------------')
        adjust = -1
    elif original < ending:
#        print('+++++++++++++++++++++++++++++++++++++++++++++')
        adjust = 1
#    print adjust
    return adjust


def getbit(adjust=0):  # 1 means record longer, -1 shorter
    data = record(1.0 / config.BITRATE + 1.0 * adjust / config.LONGERSIGNAL)
#    print '1 = ', gettonepower(config.HIGH, data)
#    print '0 = ', gettonepower(config.LOW, data)
    return 1 if getstronger(data) == config.HIGH else 0, getadjust(data)


def preambuleabsorbing():
    adjust = 0
    prevdata = None
    while True:
        data, adjust = getbit(adjust)
        if data == prevdata:
            return
        prevdata = data

def readdata():
    if detecttransmission(45):
        print 'Signal detected'
    else:
        print 'aborting'
        return
    synchronize()
    print 'Synchronized'
    preambuleabsorbing()
    print 'End of Preambule'


start = time.time()
readdata()
print time.time() - start

recorder.close()
