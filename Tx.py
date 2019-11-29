import FancyDataSender as FancyDataSender


class Tx:

    def __init__(self):
        self.dataSender = FancyDataSender.UnicastDataSender()

    def readFromPenDrive(self):
        i = 1

    def sendPacket(self, data):
        packet = self.createPacket(data, self.dataSender.sequenceNumber)
        packetSend = False
        while notpacketSend:
            notpacketSend = self.dataSender(packet)

    def createPacket(self, data, sequenceNumber):
        i = 2
