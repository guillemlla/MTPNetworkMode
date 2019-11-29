from Utils import PacketManager as pm
import random

random.seed()


def testUnicastHeaders(sequenceNumber, isACK):
    header = pm.createUnicastHeader(sequenceNumber, isACK)
    sequenceNumber2, isACK2 = pm.readUnicastHeader(header)
    if sequenceNumber == sequenceNumber2 and isACK == isACK2:
        return True
    return False


def testUnicastPacket(payload, sequenceNumber, isACK):
    packet = pm.createUnicastPacket(payload, sequenceNumber, isACK)
    payload2, sequenceNumber2, isACK2 = pm.readUnicastPacket(packet)
    if payload == payload2 and sequenceNumber == sequenceNumber2 and isACK == isACK2:
        return True
    return False

N = 4
result = [False for i in range(0, N)]
result[0] = testUnicastHeaders(0, False)
result[1] = testUnicastHeaders(0, True)
result[2] = testUnicastHeaders(1, False)
result[3] = testUnicastHeaders(1, True)

containsFalse = result.__contains__(False)
if containsFalse:
    print("Something Bad in 1T1 Headers")
else:
    print("1T1 headers OK")

N = 4
result = [False for i in range(0, N)]
result[0] = testUnicastPacket("Hola", 0, False)
result[1] = testUnicastPacket("12345", 0, False)
result[2] = testUnicastPacket("MTP group C 2019 %", 0, False)
result[3] = testUnicastPacket("2178391237123710", 0, False)

containsFalse = result.__contains__(False)
if containsFalse:
    print(result)
    print("Something Bad in 1T1 Packet")
else:
    print("1T1 packet OK")


def testNetworkCreateHeader(source1, dest1, dest2, isACK, sequenceNumber, packetType, valueExcpected):
    header = pm.createNetworkHeader(source1, dest1, dest2, isACK, sequenceNumber, packetType)
    print("Value expected: ", valueExcpected[0], valueExcpected[1], " Actual value: ", header[0], header[1])


def testNetworkHeaders(source, dest1, dest2, isACK, sequenceNumber, packetType):
    header = pm.createNetworkHeader(source, dest1, dest2, isACK, sequenceNumber, packetType)
    source2, dest12, dest22, isACK2, sequenceNumber2, packetType2 = pm.readNetworkHeader(header)
    # print(source2, dest12, dest22, isACK2, sequenceNumber2, packetType2)
    if source == source2 and dest1 == dest12 and dest2 == dest22 and isACK == isACK2 \
            and sequenceNumber == sequenceNumber2 and packetType == packetType2:
        return True
    return False


def testNetworkPacket(payload, source, dest1, dest2, isACK, sequenceNumber, packetType):
    return True





N = 10
result = [False for i in range(0, N)]
i = 0
while i < N:
    source = random.randint(0, 15)
    dest1 = random.randint(0, 15)
    dest2 = random.randint(0, 15)
    isACK = pm.numToBool(random.randint(0, 1))
    sequenceNumbers = random.randint(0, 1)
    packetType = random.randint(0, 3)
    # print('Test Network ', i)
    data = ' (', source, ' ,', dest1, ' ,', dest2, ' ,', isACK, ' ,', sequenceNumbers, ' ,', packetType, ')'
    # print(data)
    result[i] = testNetworkHeaders(source, dest1, dest2, isACK, sequenceNumbers, packetType)
    i = i + 1

containsFalse = result.__contains__(False)
if containsFalse:
    print("Something Bad")
else:
    print("Network headers OK")





