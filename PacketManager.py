from Support import Exceptions, Constants as CTE
import array


def createUnicastPacket(payload, sequenceNumber, isACK):
    if type(payload) == int:
        payload = str(payload)
    header = createUnicastHeader(sequenceNumber, isACK)
    data = [header]
    payloadBinary = array.array('B', payload).tolist()
    data.extend(payloadBinary)
    if len(data) <= CTE.PACKET_SIZE:
        return data
    else:
        raise Exceptions.WrongPayloadSize()


# HEADER
# 00:0-> packet 0 01:1->ACK packet 0
# 10:2-> packet 1 11:3 -> ACK packet 1
def createUnicastHeader(sequenceNumber, isACK):
    header = boolToNum(isACK) + (sequenceNumber << 1)
    return header


def readUnicastPacket(packet):
    sequenceNumber, isACK = readUnicastHeader(packet[0])
    payload = packet[1:len(packet)]
    payload = arrayToString(payload)
    return payload, sequenceNumber, isACK


def arrayToString(arrayBytes):
    new = ""
    for x in arrayBytes:
        new += chr(x)
    return new


def readUnicastHeader(header):
    sequenceNumber = header >> 1
    isACK = header & 0x1
    return sequenceNumber, numToBool(isACK)


def createNetworkPacket(payload, source, dest1, dest2, isACK, sequenceNumber, packetType):
    data = createNetworkHeader(source, dest1, dest2, isACK, sequenceNumber, packetType)
    payloadBinary = array.array('B', payload).tolist()
    data.extend(payloadBinary)
    if len(data <= CTE.PACKET_SIZE):
        return data
    else:
        raise Exceptions.WrongPayloadSize()


def readNetworkPacket(packet):
    source, dest1, dest2, isACK, sequenceNumber, packetType = readNetworkHeader(packet[0:2])
    payload = packet[2:len(packet)]
    return payload, source, dest1, dest2, isACK, sequenceNumber, packetType


def createNetworkHeader(source, dest1, dest2, isACK, sequenceNumber, packetType):
    first = source << 4 | dest1
    second = (boolToNum(isACK) << 7) | (sequenceNumber << 6) | (dest2 << 2) | packetType
    return [first, second]


def readNetworkHeader(header):
    source = header[0] >> 4
    dest1 = header[0] & 15
    isACK = header[1] >> 7
    sequenceNumber = (header[1] >> 6) & 1
    dest2 = (header[1] >> 2) & 15
    packetType = header[1] & 3
    return source, dest1, dest2, numToBool(isACK), sequenceNumber, packetType

def createReplyYesPacket(dest):
    packet = createNetworkPacket(CTE.NETWORK_PAQUET_CONTROL_REPLY_YES_PAYLOAD, CTE.IP_ADDRESS, dest,
                                 dest, CTE.PAQUET_FIELD_ISACK_YES_ACK, CTE.PAQUET_FIELD_SN_FIRST,
                                 CTE.NETWORK_PAQUET_TYPE_CONTROL)
    return packet

def createReplyNoPacket(dest):
    packet = createNetworkPacket(CTE.NETWORK_PAQUET_CONTROL_REPLY_NO_PAYLOAD, CTE.IP_ADDRESS, dest,
                                 dest, CTE.PAQUET_FIELD_ISACK_NO_ACK, CTE.PAQUET_FIELD_SN_FIRST,
                                 CTE.NETWORK_PAQUET_TYPE_CONTROL)
    return packet

def boolToNum(boolVar):
    mapper = {
        False: 0,
        True: 1
    }
    return mapper[boolVar]


def numToBool(num):
    mapper = {
        0: False,
        1: True
    }
    return mapper[num]
