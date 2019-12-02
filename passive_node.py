import Support.Constants as CTE
import time
import random
import Tx as tx
from Utils.PacketManager import readNetworkPacket, createNetworkPacket
from ModeControllers.NetworkMode import isFileAlreadyReceived


TIMEOUT_MAX2SEND = 1000   # one second

def check_recive_hello(receiver):
    ret = False
    msg_rcv = receiver.receivePacket
    payload, source, dest1, dest2, isACK, sequenceNumber, packetType = readNetworkPacket(msg_rcv)

    if (packetType == CTE.NETWORK_PAQUET_TYPE_CONTROL & payload == CTE.NETWORK_PAQUET_CONTROL_HELLO_PAYLOAD):
        ret = True

    return ret, source

def passive_node(transmiter, receiver, hist):
    FileAlreadyReceived = isFileAlreadyReceived()
    IsHello, NextRcv = check_recive_hello( receiver )
    if( IsHello ):
        if( FileAlreadyReceived ):
            #reply NO
            time.sleep(random.randint(0, TIMEOUT_MAX2SEND) / 1000.0)
            packet = createNetworkPacket(CTE.NETWORK_PAQUET_CONTROL_REPLY_NO_PAYLOAD, CTE.IP_ADDRESS, NextRcv, NextRcv, CTE.PAQUET_FIELD_ISACK_NO_ACK, CTE.PAQUET_FIELD_SN_FIRST, CTE.NETWORK_PAQUET_TYPE_CONTROL)
        else:
            # reply YES
            time.sleep(random.randint(0,TIMEOUT_MAX2SEND)/1000.0)
            packet = createNetworkPacket(CTE.ETWORK_PAQUET_CONTROL_REPLY_YES_PAYLOAD, CTE.IP_ADDRESS, NextRcv, NextRcv, CTE.PAQUET_FIELD_ISACK_YES_ACK, CTE.PAQUET_FIELD_SN_FIRST, CTE.NETWORK_PAQUET_TYPE_CONTROL)
        tx.sendPacket(packet)

    return FileAlreadyReceived
