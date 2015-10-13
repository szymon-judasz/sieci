#!/usr/bin/env python
# vim:ts=4:sts=4:sw=4:expandtab

import sys
import wave
import numpy

import pulseaudio as pa
#out = []
#with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=44100, channels=1) as player:
#    for x in range(0,440):
#        out = numpy.sin(440.0 / 44100 * 2 * numpy.pi * numpy.array(range(0,100)))*32000
#        player.write(out.astype(numpy.int16).tostring())
#    player.drain()

#BUG, when time is shorter than 1/freq then there is no sound
def playtone(freq, amplitude, time):
    tab = []
    with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE, rate=44100, channels=1) as player:
        for x in range(0,int(freq*time)):
            tab = numpy.sin(freq / 44100.0 * 2 * numpy.pi * numpy.array(range(0,44100/freq)))*amplitude
            player.write(tab.astype(numpy.int16).tostring())
        player.drain()

def generaterawdata(freq, amplitude, time):
    tab = (numpy.sin(freq / 44100.0 * 2 * numpy.pi * numpy.array(range(0,44100/freq)))*amplitude).astype(numpy.int16)
    return tab
