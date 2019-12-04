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

MAX_RETRIES = 3
REPLY_YES = "Yes"
ACK_RECEIVED = True

node_list = [1, 2, 3, 4, 5, 6, 7, 8]

class Network_Mode:

	def __init__(self, receiver, transmitter, own_address):
		self.receiver = receiver
		self.transmitter = transmitter
		self.historical_data = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0}
		self.file_already_received = False
		self.active_state = False
		self.finished = False
	
	def network_mode(self):
		# State shows if the node is active or not
		# Check if there is a USB connected
		rpistr = "ls /media/pi"
		USB_name = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid,stdout=subprocess.PIPE)
		line = USB_name.stdout.readline()
		
		if USB_connected():
			self.active_state = True
			self.update_token()

		
		# Set node active or pasive
		while not self.finished:
			if self.active_state:
				self.active_node()
			else:
				self.passive_node()


	def active_node(self):
		# We obtain the nodes to send data through the different mechanisms implemented on the standard
		# Save data from USB
		data_usb = read_file()

		# List of nodes which replied Yes to Hello message
		reply_yes_node = []
		
		reply_no_node = []
		# List of nodes which received the packet of data
		nodes_with_packet = []
		
		everyoneHasTheToken, reply_yes_node, reply_no_node, nodes_with_packet = self.polling(data_usb)

		# Pass token to one of the nodes with data
		if everyoneHasTheToken:
			self.finished = True
		else:
			ack = False
			for n in nodes_with_packet:
				send_token_retries = 0
				while send_data_retries < MAX_RETRIES:
					ack = self.send_token(n)
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
						time.sleep(random.randint(0,TIMEOUT_MAX2SEND)/1000.0)
					tx.sendPacket(packet)

			elif packetType == CTE.NETWORK_PAQUET_TYPE_PASSTOKEN:
				if dest1 == dest2:
					if self.file_already_received:
						packet = PM.createReplyYesPacket(next_rcv)
						self.active_state = True
					else:
						packet = PM.createReplyNoPacket(next_rcv)
					tx.sendPacket(packet)
				else:
					self.send_token(dest2)
			elif packetType == CTE.NETWORK_PAQUET_TYPE_DATA:
					write_USB(payload)
			

	def send_token(self, new_token_owner):
		packet = pm.createNetworkPacket(self.history_to_string(self.historical_data), FancyDataSender.BaseDataSender.address, new_token_owner, new_token_owner, False, 0, CTE.NETWORK_PAQUET_TYPE_PASSTOKEN)
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
		
		
	def polling(self, data_usb):
		ID = FancyDataSender.BaseDataSender.address
		thereIsReply = False
		timeout = 5
		reply_yes_node = []
		nodes_with_packet = []
		reply_no_node = []
		for x in range(1,8) :
			dest1 = x
			dest2 = x
			if dest1 != ID :
				data = PacketManager.createNetworkPacket(CTE.NETWORK_PAQUET_CONTROL_HELLO_PAYLOAD,source,dest1,dest2,0,0,CTE.NETWORK_PAQUET_TYPE_CONTROL)            
                self.transmitter.sendData(data)
				time_first = time.time()
				while True :
					response = self.receiver.receiveMessage()
					time_actual = time.time()
					if time_actual >=  time_first + timeout:
						break
					if response is not None :
						#From received data take an integer number:
						payload, _, _, _, _, _, packetType = pm.readNetworkPacket(response)
						if (packetType == CTE.NETWORK_PAQUET_TYPE_CONTROL and dest1 == ID):
							if (payload == CTE.NETWORK_PAQUET_CONTROL_REPLY_YES_PAYLOAD):  #Received reply yes
								thereIsReply = True
								# Do whatever: SEND FILE to dest1
								reply_yes_node.append(dest1)
								ack = self.send_file(dest1, data_usb)
								if ack:
									nodes_with_packet.append(dest1)
							elif (payload == CTE.NETWORK_PAQUET_CONTROL_REPLY_NO_PAYLOAD) :
								reply_no_node.append(dest1)
							break
	   
		if thereIsReply == False :
			everyoneHasTheToken = check_token(self.history_to_string(self.historical_data))
		return everyoneHasTheToken, reply_yes_node, reply_no_node, nodes_with_packet
                
	def check_token(self, token) :
		for x in range(0,15) :
			if ((x % 2) != 0) :
				if (token[x] == 0) :
					return False
		return True
		
	def history_to_string(self):
		history = None
		for k in self.historical_data.keys():
			history = history + str(self.historical_data.get(k))+k
		return history

	def send_data(self, transmitter, receiver, data_usb):
		# Sends data from USB to the nodes which replied Yes to a Hello message
		data = pm.createNetworkPacket(data_usb, transmitter, receiver, receiver, False, 0, CTE.NETWORK_PAQUET_TYPE_DATA)
		# Sends the packet with the information from file at USB
		ack = tx.sendPacket(self, data)

		return ack