from Utils import FancyDataSender as FancyDataSender


class Rx:

    def __init__(self):
        self.dataSender = FancyDataSender.UnicastDataSender()

    def writeInPen(self):
        i = 1

    def recievePacket(self):
        message = self.dataSender.receiveMessage()


