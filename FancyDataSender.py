import Constants as CTE
from lib_nrf24 import NRF24
import RPi.GPIO as GPIO
import signal, spidev, time


class BaseDataSender:

    def __init__(self, address):
        self.sequenceNumber = 0
        self.numPackets = 0
        self.address = address
        self.radio = self.initRadio()
        self.sequenceNumber = -1
        self.numPackets = -1

    def sendData(self, data):
        self.radio.stopListening()
        self.radio.write(data)
        print("[*] Packet ", self.numPackets, " Send")
        self.radio.startListening()
        return self.waitForACK()

    def waitForACK(self):
        signal.signal(signal.SIGALRM, self.timeoutHandler)
        signal.alarm(CTE.TIMEOUT)
        try:
            file = self.receiveMessage()
            while not self.isCorrectACK(file):
                file = self.receiveMessage()
            signal.alarm(0)
            self.changeSequenceNumber()
            return True
        except TimeoutError:
            return False

    def receiveMessage(self):
        while not self.radio.available(CTE.PIPES[1]):
            time.sleep(1000 / 1000000)
        file = []
        self.radio.read(file, self.radio.getPayloadSize())
        return file

    def timeoutHandler(self):
        print("[*] Packet ", self.numPackets, " Timeout")
        raise TimeoutError()

    def changeSequenceNumber(self):
        if self.sequenceNumber == 0:
            self.sequenceNumber = 1
        else:
            self.sequenceNumber = 0

    def isCorrectACK(self,data):
        raise NotImplementedError

    @staticmethod
    def initRadio():
        GPIO.setmode(GPIO.BCM)
        radio = NRF24(GPIO, spidev.SpiDev())
        print("[*] Starting Radio Interface...")
        radio.begin(CTE.BEGIN[0], CTE.BEGIN[1])
        radio.setRetries(CTE.RETRY[0], CTE.RETRY[1])
        radio.setPayloadSize(CTE.PAYLOAD_SIZE)
        radio.setChannel(CTE.CHANNEL)
        radio.setDataRate(CTE.DATARATE)
        radio.setPALevel(CTE.PA_LEVEL)
        radio.setAutoAck(CTE.AUTO_TRACK)
        radio.enableDynamicPayloads()
        radio.enableAckPayload()
        radio.openWritingPipe(CTE.PIPES[0])
        radio.openReadingPipe(1, CTE.PIPES[1])
        radio.startListening()
        radio.stopListening()
        # radio.printDetails()
        return radio


class NetworkDataSender(BaseDataSender):
    def isCorrectACK(self, data):
        source, dest1, dest2, isACK, sequenceNumber, packetType = PacketManager.readNetworkHeader(data)
        if isACK and dest2 == self.address:
            return True


class UnicastDataSender(BaseDataSender):
    def isCorrectACK(self, data):
        sequenceNumber, isACK = PacketManager.readUnicastHeader(data)
        if isACK and sequenceNumber == self.sequenceNumber:
            return True
        else:
            return False
