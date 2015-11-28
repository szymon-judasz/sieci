#!/usr/bin/env python
__author__ = 'Szymon Judasz'
import numpy
import config
import pulseaudio as pa
import PacketFactory as pf

samplerate = 44100


def generaterawdata(freq, amplitude, time):
    tab = (numpy.sin((freq + 0.0) / samplerate * 2 * numpy.pi * numpy.array(
        range(0, numpy.ceil(samplerate * time).astype(int)))) * amplitude).astype(
        numpy.int16)
    return tab


lowsignal = generaterawdata(config.LOW, config.AMPLITUDE, 1.0/config.BITRATE).astype(numpy.int16).tostring()
highsignal = generaterawdata(config.HIGH, config.AMPLITUDE, 1.0/config.BITRATE).astype(numpy.int16).tostring()


def senddata(source):
    with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=samplerate, channels=1) as player:
        for i in range(0, len(source)):
            if source[i] == 1:
                player.write(highsignal)
            else:
                player.write(lowsignal)
        player.drain()

senddata(pf.buildPacket(51, 23, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'))
