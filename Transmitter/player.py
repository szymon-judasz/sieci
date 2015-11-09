#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import numpy
import config
import time
import pulseaudio as pa
import PacketFactory as pf


# TODO: hardcode low and high signal tables, don't calcualte them in playtone
# TODO: open and close stream

def playtone(freq, amplitude, time):
    with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=44100, channels=1) as player:
        for x in range(0, int(freq * time)):
            tab = numpy.sin(freq / 44100.0 * 2 * numpy.pi * numpy.array(range(0, 44100 / freq))) * amplitude
            player.write(tab.astype(numpy.int16).tostring())
        player.drain()


def generaterawdata(freq, amplitude, time):
    tab = (numpy.sin(freq / 44100.0 * 2 * numpy.pi * numpy.array(
        range(0, numpy.ceil(44100 * time).astype(int)))) * amplitude).astype(
        numpy.int16)
    return tab


lowsignal = generaterawdata(config.LOW, config.AMPLITUDE, config.BITRATE).astype(numpy.int16).tostring()
highsignal = generaterawdata(config.HIGH, config.AMPLITUDE, config.BITRATE).astype(numpy.int16).tostring()


def sendData(source):
    with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=44100, channels=1) as player:
        for i in range(0, len(source)):
            if source[i] == 1:
                print('1')
                player.write(highsignal)
            else:
                print('0')
                player.write(lowsignal)
        player.drain()
        player.close()


x = pf.nrzi(pf.inttobyte(1023, 10))

while 1 == 1:
    sendData(pf.buildPacket(10, 10, "ala"))
