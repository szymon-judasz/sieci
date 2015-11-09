__author__ = 'Z500User'
ADDRESS_SIZE = 8
ADDRESS_FIRST = True
PREAMBLE = 0xAAAAAAAAAAAAAAAB
PREAMBLE_SIZE = 16 * 4  # 16 nibble w preambule

CODING = {0: 0b011110, 1: 0b01001, 2: 0b010100, 3: 0b010101, 4: 0b01010, 5: 0b01011, 6: 0b01110, 7: 0b01111,
          8: 0b010010, 9: 0b010011, 10: 0b010110, 11: 0b010111, 12: 0b011010, 13: 0b011011, 14: 0b011100, 15: 0b011101}

CRC = 0x04C11DB7
CRCSIZE = 8 * 4  # rozmiar CR

# czestotliwosci sygnalow wysoki/niski
HIGH = 880
LOW = 440


# jak glosno nadawac
AMPLITUDE = 32000

# jak glosny musi byc sygnal, by byl sygnalem
THRESHOLD = 10000000
# predkosc transmisji
BITRATE = 1

NRZI_START = 0 # ktory bit startuje w nrzi
