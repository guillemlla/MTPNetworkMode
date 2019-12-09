#!/usr/bin/env python

# Import of libraries from python
import os
import subprocess
import random
import sys
import time

# Import of libraries implemented for the Network Protocol implementation
import Rx as rx
import Tx as tx
import PacketManager as pm
import Constants as CTE
import FancyDataSender as BaseDataSender
import USBManager

MAX_RETRIES = 3
REPLY_YES = "Yes"
ACK_RECEIVED = True

node_list = [1, 2, 3, 4, 5, 6, 7, 8]


class Network_Mode:
    def __init__(self, receiver, transmitter, own_address):
        self.receiver = receiver
        self.transmitter = transmitter
        self.historical_data = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
        self.file_already_received = False
        self.active_state = False
        self.finished = False
        self.iam_the_first = False
        self.data = None

    def network_mode(self):
        # State shows if the node is active or not
        #  Check if there is a USB connected
        # rpistr = "ls /media/pi"
        #USB_name = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE)
        #line = USB_name.stdout.readline()
        
        if not os.path.exists("/home/pi/network_file"):
            os.makedirs("/home/pi/network_file")
        
        if len(os.listdir(os.path.dirname( "/media/pi/")))!=0:
            self.data = USBManager.read_file_usb()
            USBManager.copyfile(self.data,"/home/pi/network_file/data.txt")
            self.active_state = True
            self.update_token()
            self.iam_the_first = True

        # Set node active or pasive
        while not self.finished:
            if self.active_state:
                self.active_node()
            else:
                self.passive_node()

    def active_node(self):
        # We obtain the nodes to send data through the different mechanisms implemented on the standard
        # Save data from USB

        file2send = self.data   #ha d'estar guardada a una variable de quan l'ha rebut



        # List of nodes which replied Yes to Hello message
        reply_yes_node = []
        # List of nodes which replied No to Hello message
        # reply_no_node = []
        #  List of nodes which received the packet of data
        # nodes_with_packet = []

        everyoneHasTheToken, reply_yes_node, reply_no_node, nodes_with_packet = self.polling(file2send)

        # Pass token to one of the nodes with data
        if everyoneHasTheToken:
            self.finished = True
        else:
            ack = False
            if(len(nodes_with_packet!=0)):

                ##se puede crear funcion que haga este for pasando por parametro la lista de nodos, porque se hace en varios casos,
                for n in nodes_with_packet:
                    send_token_retries = 0
                    while send_data_retries < MAX_RETRIES:
                        ack = self.send_token(n, n)
                        if ack:
                            send_data_retries = MAX_RETRIES + 1
                            self.active_state = False
                    if ack:
                        break
            else:
                nodes_notoken_neigh, nodes_notoken_far = check_nodes_no_token(self.history_to_string(self.historical_data), reply_no_node)

                if(len(nodes_notoken_neigh==0)):

                    for n in nodes_notoken_far:
                        send_token_retries = 0
                        while send_data_retries < MAX_RETRIES:


                            ack = self.send_token(n, whosentMeToken)
                            if ack:
                                send_data_retries = MAX_RETRIES + 1
                                self.active_state = False
                        if ack:
                            break
                else:
                    for n in nodes_notoken_neigh:
                        send_token_retries = 0
                        while send_data_retries < MAX_RETRIES:
                            ack = self.send_token(n, n)
                            if ack:
                                send_data_retries = MAX_RETRIES + 1
                                self.active_state = False
                        if ack:
                            break



    def passive_node(self):
        msg_rcv = receiver.receivePacket()
        payload, next_rcv, dest1, dest2, isACK, sequenceNumber, packetType = PM.readNetworkPacket(msg_rcv)

        if dest1 == FancyDataSender.BaseDataSender.address:
            if packetType == CTE.NETWORK_PAQUET_TYPE_CONTROL:
                if payload == CTE.NETWORK_PAQUET_CONTROL_HELLO_PAYLOAD:
                    if self.file_already_received:
                        packet = PM.createReplyNoPacket(next_rcv)
                        time.sleep(random.randint(0, TIMEOUT_MAX2SEND) / 1000.0)
                    else:
                        packet = PM.createReplyYesPacket(next_rcv)
                        time.sleep(random.randint(0, TIMEOUT_MAX2SEND) / 1000.0)
                    tx.sendPacket(packet)

            elif packetType == CTE.NETWORK_PAQUET_TYPE_PASSTOKEN:
                #TODO
                if dest1 == dest2:
                    if self.file_already_received:
                        #to do  should send ACK, not reply yes
                        #packet = PM.createReplyYesPacket(next_rcv)
                        self.active_state = True
                    tx.sendPacket(packet)
                else:
                    #not finished, the gateway  may not be dest2 ( because maybe this node does not have direct contact with it), should check this in table of  replies_yes_no
                    self.send_token(dest2, dest2)
            elif packetType == CTE.NETWORK_PAQUET_TYPE_DATA:
                #not write sub, write locally First
                #create ack packet and send it
                ################save payload or msg_recveive in data
                self.data = self.data + payload
                #si el paquet es l'ultim o diu END o alguna cosa per l'estil que el guardi amb:
                #USBManager.copyfile(self.data,"/home/pi/network_file/data.txt")
                #USBManager.save to usb if usb connected



    def send_token(self, new_token_owner, gateway):
        packet = pm.createNetworkPacket(self.history_to_string(self.historical_data),FancyDataSender.BaseDataSender.address, gateway, new_token_owner, False, 0, CTE.NETWORK_PAQUET_TYPE_PASSTOKEN)
        ack = tx.sendPacket(self, packet)
        return ack

    def update_token(self):
        self.historical_data[FancyDataSender.BaseDataSender.address] = 1

    def send_hello(self, transmitter, dest):
        hello_msg = "Hello"
        # According to standard: Control: 00, Data: 01, Token:10
        data = pm.createNetworkPacket(hello_msg, FancyDataSender.BaseDataSender.address, dest, dest, False, 0, CTE.NETWORK_PAQUET_TYPE_CONTROL)
        # Send data and wait for Reply Yes
        # Place here the function that sends the data and checks whether it's Reply YES or NO or timeout has occurred
        reply = tx.sendPacket(self, data)
        # returns True/False or Yes/No according if data has been successfully send or not
        return reply

    def polling(self, file2send):
        ID = FancyDataSender.BaseDataSender.address
        thereIsReply = False
        timeout = 5
        reply_yes_node = []
        nodes_with_packet = []
        reply_no_node = []
        for x in range(1, 8):
            dest1 = x
            dest2 = x
            source = ID
            if dest1 != ID:
                #create hello packet
                data = PacketManager.createNetworkPacket(CTE.NETWORK_PAQUET_CONTROL_HELLO_PAYLOAD, source, dest1, dest2, 0, 0, CTE.NETWORK_PAQUET_TYPE_CONTROL)
                #send hello packet
                ack = tx.sendPacket(self, data)

                time_first = time.time()
                while True:
                    response = self.receiver.receiveMessage()
                    time_actual = time.time()
                    #LO DEL TIMEOUT NO S'HAURIA DE GESTIONAR DINS DE RECEIVE MESSAGE?
                    if time_actual >= time_first + timeout:
                        break
                    if response is not None:
                        #
                        payload, source, dest, _, _, _, packetType = pm.readNetworkPacket(response)
                        if (packetType == CTE.NETWORK_PAQUET_TYPE_CONTROL and dest == ID):
                            if (payload == CTE.NETWORK_PAQUET_CONTROL_REPLY_YES_PAYLOAD):  # Received reply yes
                                thereIsReply = True
                                # SEND FILE to dest1 of the hello packet/source of the reply packet
                                reply_yes_node.append(dest1)
                                #send whole file
                                ack = self.send_file(ID, dest1, file2send)
                                self.file_already_received=True
                                #ACK WILL BE TRUE IF THE FILE HAS BEEN CORRECTLY SENT  (INSIDE SEND_FILE, RETRANSMISSIONS SHOULD BE HANDLED
                                if ack:
                                    nodes_with_packet.append(dest1)

                            elif (payload == CTE.NETWORK_PAQUET_CONTROL_REPLY_NO_PAYLOAD):
                                reply_no_node.append(dest1)
                            break


        if not thereIsReply:
            everyoneHasTheToken = False
            everyoneHasTheToken = check_token(self.history_to_string(self.historical_data))
        return everyoneHasTheToken, reply_yes_node, reply_no_node, nodes_with_packet


#checks if at least there's a node that has not received the token
def check_token(self, token):
    for x in range(0, 16):
        if ((x % 2) != 0):
            if (token[x] == "0"):
                return False
    return True


def check_nodes_notoken(self, token, nodes_replied_no):
    nodes = []
    for x in range(0, 16):
        if ((x % 2) != 0):
            if (token[x] == "0"):
                if token[x-1] in nodes_replied_no:
                    nodes_neigh.append(token[x-1])
                else:
                    nodes_far.append(token[x-1])
    return nodes_neigh, nodes_far

#converts dictionary to string
def history_to_string(self):
    history = ""
    keys = self.historical_data.keys()
    for k in keys:
        history = history + str(k) + str(data.get(k))
    return history


#ONLY SENDS ONE PACKET of ddT
def send_data(self, transmitter, receiver, data):
    data = pm.createNetworkPacket(data, transmitter, receiver, receiver, False, 0, CTE.NETWORK_PAQUET_TYPE_DATA)
    ack = tx.sendPacket(self, data)

    return ack


#send whole file
def send_file(self, tx, rx, data):
    i = 0
    while i< len(data):
        if i+30>len(data):
            data2send = data[i:len(data)]
        else:
            data2send = data[i:i+30]

        ack = send_data(self, tx, rx, data2send)

        #gestionar restransmissions
        i=0
        while not ack:
            if( i== 3):
                return False
            ack = send_data(self, tx, rx, data2send)


        i+=30

    return True

