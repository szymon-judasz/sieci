#!/usr/bin/env python
__author__ = 'Szymon Judasz'
ADDRESS_SIZE = 8
ADDRESS_FIRST = True
PREAMBLE = 0xAAAAAAAB
PREAMBLE_SIZE = 8 * 4  # 16 nibble w preambule

CODING = {0: 0b011110, 1: 0b01001, 2: 0b010100, 3: 0b010101, 4: 0b01010, 5: 0b01011, 6: 0b01110, 7: 0b01111,
          8: 0b010010, 9: 0b010011, 10: 0b010110, 11: 0b010111, 12: 0b011010, 13: 0b011011, 14: 0b011100, 15: 0b011101}

CRC = 0x04C11DB7
CRCSIZE = 8 * 4  # rozmiar CRC

EOM = 0b01101
EOMSIZE = 5

# czestotliwosci sygnalow wysoki/niski
HIGH = 880
LOW = 440

LONGERSIGNAL = LOW if LOW < HIGH else HIGH

# jak glosno nadawac
AMPLITUDE = 32000

# jak glosny musi byc sygnal, by byl sygnalem
THRESHOLD = 10000000
BITRATE = 40

NRZI_START = 0 # ktory bit startuje w nrzi


if ADDRESS_SIZE % 4 != 0:
    raise Exception('Invalid config. Address size must be divisible by 4')
if LOW < 1.1 * HIGH and LOW > 0.9 * HIGH:
    raise Exception('Low and High signal frequencies are similar. Bugs will occur')
if BITRATE > 45:
    print 'Runing at unsafe bandwidth'
if LOW > 16000 or HIGH > 16000:
    print 'Caution. Signals at very high frequency. Bugs may occur'
if LOW < 30 or HIGH < 30:
    print 'Caution. Signals at very low frequency. Bugs may occur'
