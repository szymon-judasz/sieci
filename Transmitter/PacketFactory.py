__author__ = 'Z500User'
import config


def inttobyte(address, size):
    """

    :param address: int number to be convered to binary representation
    :return: list of 0 and 1
    """
    if 2 ** size <= address or address < 0 or not (type(address) is int or type(address) is long):
        raise Exception('Invalid address')

    result = list()
    x = address
    while x > 0:
        if x % 2 == 1:
            result.append(1)
        else:
            result.append(0)
        x /= 2
    while len(result) < size:
        result.append(0)
    result.reverse()
    return result


def createrawpacket(sourceAddress, destinationAddress, data):
    """
    source address, destination address and data, without crc, and 5-4
    :param sourceAddress: list
    :param destinationAddress: list
    :param data: list or str
    :return:
    """
    result = list()

    if config.ADDRESS_FIRST:
        result.extend(inttobyte(sourceAddress, config.ADDRESS_SIZE))
        result.extend(inttobyte(destinationAddress, config.ADDRESS_SIZE))
    else:
        result.extend(inttobyte(destinationAddress, config.ADDRESS_SIZE))
        result.extend(inttobyte(sourceAddress, config.ADDRESS_SIZE))

    if type(data) is str:
        for c in data:
            result.extend(inttobyte(ord(c), 8))
    else:
        result.extend(data)
    return result


def attachPreamble(source):
    result = source
    preamble = config.PREAMBLE
    preamble = inttobyte(preamble, config.PREAMBLE_SIZE)
    result.reverse()
    preamble.reverse()
    result.extend(preamble)
    result.reverse()
    return result


def fddi(source):
    data = list(source)
    if not len(data) % 4 == 0:
        raise Exception('Source size not divisible by 4')
    result = list()
    while len(data) > 0:
        val = 8 * data[0] + 4 * data[1] + 2 * data[2] + data[3]
        del data[0]
        del data[0]
        del data[0]
        del data[0]
        result.extend(inttobyte(config.CODING[val], 5))
    return result


def computeCRC(source):
    data = list(source)
    for i in range(0, config.CRCSIZE):
        data.append(0)

    mask = inttobyte(config.CRC, config.CRCSIZE)

    for i in range(0, len(data) - config.CRCSIZE):
        if data[i] == 1:
            data[i] = 0
            for j in range(1, config.CRCSIZE + 1):
                data[i + j] = data[i + j] ^ mask[j - 1]
    result = list()
    for i in range(0, config.CRCSIZE):
        result.append(data[len(data) - 1])
        del data[len(data) - 1]
    result.reverse()

    source.extend(result)
    return source


def nrzi(source):
    data = config.NRZI_START
    result = list()
    for i in source:
        if i == 1:
            data = 1 - data
        result.append(data)
    return result


def buildPacket(sourceAddress, destinationAddress, data):
    return attachPreamble(nrzi(fddi(computeCRC(createrawpacket(sourceAddress, destinationAddress, data)))))
