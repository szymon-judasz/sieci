#!/usr/bin/env python
__author__ = 'Szymon Judasz'
import numpy as np
import config
import pulseaudio as pa
import PacketFactory as pf

samplerate = 44100


def record(probeduration):
    data = np.fromstring(recorder.read(int(samplerate * probeduration) * 2), np.int16)
    return data


def quickfft(data):
    d = np.absolute(np.fft.fft(data)).astype(int)
    return d


def gettonepower(tone, data):
    fft = quickfft(data)
    return np.max(tabdrift(fft, int(tone * len(data) / samplerate) - 3, 6))


def detecttransmission(timeout=15):
    tryno = timeout * config.BITRATE
    while tryno > 0:
        data = record(5.0 / config.BITRATE)
        lowpower = gettonepower(config.LOW, data)
        highpower = gettonepower(config.HIGH, data)
        if lowpower > config.THRESHOLD or highpower > config.THRESHOLD:
            return True
        tryno -= 1
    return False


def tabdrift(source, padding,
             windowsize=samplerate / config.BITRATE):
    source = np.array(source)
    x = np.split(source, [padding, padding + windowsize])
    return x[1]


def getstronger(source):  # getstronger(record(time))
    return config.HIGH if gettonepower(config.HIGH, source) > gettonepower(config.LOW, source) else config.LOW


def synchronize():
    data = record(2.0 / config.BITRATE)
    windowsize = samplerate / config.BITRATE
    cursor = 0
    offset = windowsize
    signal = getstronger(tabdrift(data, 0))
    signal = config.LOW if signal == config.HIGH else config.HIGH
    for i in range(0, 1):
        offset = int(offset / 2)
        if gettonepower(signal, tabdrift(data, cursor)) < gettonepower(signal, tabdrift(data, cursor + offset)):
            cursor += offset
    if ((cursor + 0.0) / samplerate) > 0:
        devnull = record((cursor + 0.0) / samplerate)


def getadjust(data):
    signal = getstronger(data)
    adjust = 0
    original = gettonepower(signal, data)
    begining = gettonepower(signal, tabdrift(data, 0, 0.9 * samplerate / config.BITRATE))
    ending = gettonepower(signal, tabdrift(data, 0.1 * samplerate / config.BITRATE, 0.9 * samplerate / config.BITRATE))
    if original < begining:
        adjust = -1
    elif original < ending:
        adjust = 1
    return adjust


def getbit(adjust=0):
    data = record(1.0 / config.BITRATE + 2.0 * adjust / config.LONGERSIGNAL)
    return 1 if getstronger(data) == config.HIGH else 0, getadjust(data)


def getfivebits(adjust=0):
    result = list()
    for i in range(5):
        data, adjust = getbit(adjust)
        result.append(data)
    return result, adjust


def nrzidecodefivebits(data, lastbit):
    result = list()
    for x in data:
        result.append(1 if x != lastbit else 0)
        lastbit = x
    return result, lastbit


def bitstointcode(data):
    result = 0
    for x in data:
        result *= 2
        result = result + x
    return result


def fivebiseom(data):
    return data == config.EOM


def fivebiscorrectdata(data):
    return data in config.CODING.values()


def preambuleabsorbing():
    adjust = 0
    prevdata = None
    while True:
        data, adjust = getbit(adjust)
        if data == prevdata:
            return adjust
        prevdata = data


def fddidecoding(source):
    source = list(source)
    result = list()
    while len(source) > 0:
        x = 0
        for i in range(5):
            x *= 2
            x += source.pop(0)
        result.extend(pf.inttobyte(config.CODING.values().index(x), 4))
    return result


def readdata():  # TODO: refactor method/project structures and/or int array to string conversion
    global recorder
    recorder = pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE, rate=44100, channels=1)
    if detecttransmission(45):
        pass
    else:
        return
    print 'det'
    #synchronize()
    adjust = preambuleabsorbing()
    x = list()
    data, adjust = getfivebits(adjust)
    data, lastbit = nrzidecodefivebits(data, config.NRZI_START)
    while (not fivebiseom(bitstointcode(data))) and fivebiscorrectdata(bitstointcode(data)):
        x.extend(data)
        data, adjust = getfivebits(adjust)
        data, lastbit = nrzidecodefivebits(data, lastbit)
    if fivebiseom(bitstointcode(data)):
        pass
    elif not fivebiscorrectdata(bitstointcode(data)):
        return -1, -1, -1
    x = fddidecoding(x)
    parts = np.split(x, [len(x) - config.CRCSIZE])
    body = parts[0]

    crc = parts[1]
    expectedcrc = pf.computeCRC(body)
    if crc.tolist() != expectedcrc:
        -1, -1, -2
    x = np.split(body, [8, 16])
    address1 = x[0]
    address2 = x[1]
    message = x[2]
    address1 = bitstointcode(address1)
    address2 = bitstointcode(address2)
    result = list()
    for i in np.split(message, len(message) / 8):
        result.append(bitstointcode(i))
    recorder.close()
    return address1, address2, result

text = ''
for x in readdata()[2]:
    text += chr(x)
print(text)