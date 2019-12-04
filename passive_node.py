import Support.Constants as CTE
import Utils.PacketManager as PM
import time
import random
import Tx as tx

import NetworkMode as NM

TIMEOUT_MAX2SEND = 1000   # one second range


def passive_node(transmiter, receiver, hist):
    ChangeToActiveNode = False
    FileAlreadyReceived = NM.isFileAlreadyReceived()

    msg_rcv = receiver.receivePacket
    payload, next_rcv, dest1, dest2, isACK, sequenceNumber, packetType = PM.readNetworkPacket(msg_rcv)

    if packetType == CTE.NETWORK_PAQUET_TYPE_CONTROL:

        if payload == CTE.NETWORK_PAQUET_CONTROL_HELLO_PAYLOAD:
            if FileAlreadyReceived:
                packet = PM.createReplyNoPacket(next_rcv)
                time.sleep(random.randint(0, TIMEOUT_MAX2SEND) / 1000.0)
            else:
                packet = PM.createReplyYesPacket(next_rcv)
                time.sleep(random.randint(0,TIMEOUT_MAX2SEND)/1000.0)
            tx.sendPacket(packet)


    if packetType == CTE.NETWORK_PAQUET_TYPE_PASSTOKEN:

        if dest1 == dest2:
            if FileAlreadyReceived:
                packet = PM.createReplyYesPacket(next_rcv)
                ChangeToActiveNode = True
            else:
                packet = PM.createReplyNoPacket(next_rcv)
            tx.sendPacket(packet)
        else:
            NM.pass_token(dest2, tx)
    return ChangeToActiveNode
