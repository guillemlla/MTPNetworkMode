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

WAIT_FOR_ACK_TIME = "set time for waiting ack"
BACKOFF_TIME = "set backoff time"
MAX_RETRIES = "set maximum number of retries for a packet to be sent"

# Types of packet
CONTROL = "00"
DATA    = "01"
TOKEN   = "10"

node_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]

def network_mode(own_address):
    receiver = rx()
    transmiter = tx()
    # State ens indica si es un node actiu o no
    active_state = False

    rpistr = "ls /media/pi"
    USB_name = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE)
    line = USB_name.stdout.readline()

    # Comprovem que hi ha un usb enxufat
    if line:
        read_file_usb()
        active_state = True

    finished = False
    historical_data = None
    while not finished:
        if active_state:
            active_node(transmiter, receiver, historical_data)
        else:
            historical_data = passive_node(transmiter, receiver)


def active_node(transmiter, receiver, hist):
    # Do we need a receiver for the active node? I think the active node decides which receiver has to send packets
    # We obtain the nodes to send data through the different mechanisms implemented on the standard

    data_usb = read_file_usb()

    # List of nodes which replied Yes to Hello message
    reply_yes_node = []
    # List of nodes we received the packet of data
    nodes_with_packet = []

    # For each node on the node_list find which reply Yes to a Hello message
    for node in node_list:
        hello_retries = 0
        while hello_retries < MAX_RETRIES:
            ack = send_hello(transmiter, node)
            if ack == True:
                reply_yes_node.append(node)
                print("ACK from node {node} has been received!").format(node=node)
                # POSSIBLE implementation, but we should change the standard to send the data after receiving the
                # ACK from the Hello message
                # Send data to the nodes which replied Yes to Hello message
                # STARTS HERE
                for node_yes in reply_yes_node:
                    send_data_retries = 0
                    while send_data_retries < MAX_RETRIES:
                        ack = send_data(transmiter, node_yes, data_usb)
                        if ack == True:
                            print("ACK received!")
                            break
                        else:
                            print("ACK not received, retrying...")
                            send_data_retries += 1
                # ENDs HERE ^
                break
            else:
                print("ACK from node {node} has not been received. Retrying Hello message...").format(node=node)
                hello_retries += 1

    # Send data to the nodes which replied Yes to Hello message

    for node_yes in reply_yes_node:
        send_data_retries = 0
        while send_data_retries < MAX_RETRIES:
            ack = (send_data(transmiter, node_yes, data_usb) for node_yes in reply_yes_node)
            if ack == True:
                print("ACK received!")
                nodes_with_packet.append(node_yes)
                break
            else:
                print("ACK not received, retrying...")
                send_data_retries += 1

    source, dest1, dest2, _, sequenceNumber, packetType = (pm.readNetworkHeader() for node in node_list if reply_yes_list.index(node) == 1)

    messages = []
    # Aqui s'ha de fer lo del pooling (igual fer-ho com a funció)
    # Crec que el tema del polling està solucionat dins del FancyDataSender.py
    # JORDI: no acabo d'entendre aquesta part del codi
    while not time_out():
        receiver.receivePacket()
        new_message = receiver.message
        messages.append(new_message)
    # Aqui s'ha de fer lo del pooling

    destinations = []
    for m in messages:
        source, dest1, dest2, _, sequenceNumber, packetType = pm.readNetworkHeader(m[0:2])
        if (m[2] == CTE.NETWORK_PAQUET_CONTROL_REPLY_YES_PAYLOAD):
            destinations.append(source)


    history = hist
    new_token_owner = destinations[random.randint(len(destinations))]
    for d in destinations:
        send_file(d, transmiter)
        if d == new_token_owner:
            history = history + str(d) + "1"
        else:
            history = history + str(d) + "0"

    pass_token(new_token_owner, history, tx)

    return history


def pass_token(dest, history, tx):
    packet = pm.createNetworkPacket(history, data, dest, dest, 0, 0, CTE.NETWORK_PAQUET_TYPE_PASSTOKEN)
    tx.sendPacket(packet)


def send_file(dest, transmiter):
    pass

def send_hello(transmitter, receiver):
    hello_msg = "Hello"
    # JORDI: I can't understand exactly the usage of seq_number nor dest2
    seq_number = "To define"
    dest2 = "To define"
    # According to standard: Control: 00, Data: 01, Token:10
    data = pm.createNetworkPacket(hello_msg, transmitter, receiver, dest2, False, seq_number, CTE.NETWORK_PAQUET_TYPE_CONTROL)
    # Send data and wait for ACK
    ack = BaseDataSender.sendData(data)

    return ack

def send_data(transmitter, receiver, data_usb):
    # Sends data from usb to the nodes which replied Yes to a Hello message
    # JORDI: I can't understand exactly the usage of seq_number nor dest2
    seq_number = "To define"
    dest2 = "To define"
    data = pm.createNetworkPacket(data_usb, transmitter, receiver, dest2, False, seq_number,
                                  CTE.NETWORK_PAQUET_TYPE_DATA)
    ack = BaseDataSender.sendData(data)

    return ack

def read_file_usb():
    rpistr = "ls /media/pi"
    USB_name = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid,stdout=subprocess.PIPE)
    line = USB_name.stdout.readline()

    root = "/media/pi/" + line.rstrip().decode() + "/"
    # To be changed depending on the professor's file name
    filename = "test1m.txt"
    print(root+filename)
    copyfile = open(filename, "w+b")
    with open(root + filename) as file:
        lines = file.readlines()
        for line in lines:
            copyfile.write(line)

    print("File from USB copied!")


def write_file_usb(filename, data):
    rpistr = "ls /media/pi"
    USB_name = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid,stdout=subprocess.PIPE)
    line = USB_name.stdout.readline()

    root = "/media/pi/" + line.rstrip() + "/"
    with open(root + filename, "w+") as file:
        file.write(data)
        file.close()
