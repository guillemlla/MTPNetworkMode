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

node_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]

class Network_Mode:

	def __init__(self, receiver, transmitter, own_address):
		self.receiver = receiver
		self.transmitter = transmitter
		self.historical_data = None
	
	def network_mode(self):
		# State shows if the node is active or not
		active_state = False
		# Check if there is a USB connected
		rpistr = "ls /media/pi"
		USB_name = subprocess.Popen(rpistr, shell=True, preexec_fn=os.setsid,stdout=subprocess.PIPE)
		line = USB_name.stdout.readline()
		if line:
			active_state = True
		
		finished = False
		# Set node active or pasive
		while not finished:
			if active_state:
				self.active_node(self.transmitter, self.historical_data)
			else:
				self.passive_node(self.transmitter, self.receiver)


	def active_node(self, transmitter, token_info):
		# We obtain the nodes to send data through the different mechanisms implemented on the standard
		# Save data from USB
		data_usb = read_file_usb()

		# List of nodes which replied Yes to Hello message
		reply_yes_node = []
		# List of nodes which received the packet of data
		nodes_with_packet = []

		# For each node on the node_list find which reply Yes to a Hello message
		for node in node_list:
			hello_retries = 0
			while hello_retries < MAX_RETRIES:
				reply = self.send_hello(transmitter, node)
				# Save nodes which replied Yes to Hello message
				if reply == REPLY_YES:
					reply_yes_node.append(node)
					print("ACK from node {node} has been received!").format(node=node)
					# POSSIBLE implementation, but we should change the standard to send the data after receiving the
					# ACK from the Hello message
					# Send data to the nodes which replied Yes to Hello message
					# STARTS HERE
					for node_yes in reply_yes_node:
						send_data_retries = 0
						while send_data_retries < MAX_RETRIES:
							ack = self.send_data(transmitter, node_yes, data_usb)
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
				ack = (self.send_data(transmitter, node_yes, data_usb) for node_yes in reply_yes_node)
				if ack == ACK_RECEIVED:
					print("ACK received!")
					nodes_with_packet.append(node_yes)
					break
				else:
					print("ACK not received, retrying...")
					send_data_retries += 1

		# Pass token to one of the nodes with data
		for node in nodes_with_packet:
			ack = self.pass_token(node, transmitter, token_info)
			if ack == ACK_RECEIVED:
				# Update token
				# TODO: check if this is the proper way to update the token
				# JORDI: I think that it has to follow a sequence such as: A1B0C0D0E1F1G0H1
				# self.update_token(node, self.historical_data)
				break

		self.historical_data = self.historical_data + str(node) + "1"

	def pass_token(self, receiver, transmitter, token_info):
		packet = pm.createNetworkPacket(token_info, transmitter, receiver, 0, 0, CTE.NETWORK_PAQUET_TYPE_PASSTOKEN)
		ack = tx.sendPacket(self, packet)

		return ack

	def update_token(self, current_node, se):

	def send_hello(self, transmitter, receiver):

		hello_msg = "Hello"
		# According to standard: Control: 00, Data: 01, Token:10
		data = pm.createNetworkPacket(hello_msg, transmitter, receiver, receiver, False, 0, CTE.NETWORK_PAQUET_TYPE_CONTROL)
		# Send data and wait for Reply Yes
		# Place here the function that sends the data and checks whether it's Reply YES or NO or timeout has occurred
		reply = tx.sendPacket(self, data)
		# returns True/False or Yes/No according if data has been successfully send or not
		return reply

	def send_data(self, transmitter, receiver, data_usb):
		# Sends data from USB to the nodes which replied Yes to a Hello message
		data = pm.createNetworkPacket(data_usb, transmitter, receiver, receiver, False, 0, CTE.NETWORK_PAQUET_TYPE_DATA)
		# Sends the packet with the information from file at USB
		ack = tx.sendPacket(self, data)

		return ack
