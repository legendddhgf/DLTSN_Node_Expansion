#! /usr/bin/python
#  use carriage returns as a standard delimiter

import serial
# from dummySerial import XBee
from datetime import datetime
from time import sleep
import sys
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
from multiprocessing import Process
import binascii
from mate_interface import Mate3
# -----------------------------------------------------------------------------
# Config Settings
BROKER_NAME = "127.0.0.1"
# Config Settings
# -----------------------------------------------------------------------------

# Must be used with .encode('hex'); omitted in these functions for readability
# TODO: do we even need this?
def SertoHex(response, param):
    return response[param][2:10]
def addrToHex(response, param):
    return response[param][0:2]

# realistically this is unnecessary for simply usb communications
"""
def rxData():
    print "in rxData"
    CONST_AT = 1
    CONST_DATA = 2
    CONST_STATUS = 3
    # loop forever and read the next frame
    while True:
        try:
            print "reading frame"
            # 3 types of possible frames: AT frames, data frames, and status frames
            frameType = 0
            status = xbee.wait_read_frame()
            print status
            if 'tx_status' in status:
                if 'status' in status:
                    if status['status'] == '\x00':
                        topicStruct = ('testbed/gateway/data/' + status['source_addr'].encode('hex'))
                        publish.single(topicStruct, "RECEIVED", hostname=BROKER_NAME)
                        frameType = CONST_STATUS

            if 'rf_data' in status:
                if 'rf_data' in status:
                    t=status['rf_data'].split('\r\n')[0]
                    # t=t.split('=')[1]
                    
                    # If the response is an ND command, pass it to node discover. else, pass it to testbed/gateway/data
                    if ":" in t:
                        print "ND IN T"
                        print t
                        t = t.split(':')[1]
                        print t
                        topicStruct = ('testbed/nodeDiscover/data/' + status['source_addr'].encode('hex'))
                        publish.single(topicStruct, t, hostname=BROKER_NAME)
                        frameType = CONST_DATA
                    else:
                        print "NO ND IN T"
                        if "set" in t:
                            topicStruct = ('testbed/gateway/actuators/' + status['source_addr'].encode('hex'))
                            publish.single(topicStruct, t, hostname=BROKER_NAME)
                            frameType = CONST_DATA
                        else:
                            topicStruct = ('testbed/gateway/data/' + status['source_addr'].encode('hex'))
                            publish.single(topicStruct, t, hostname=BROKER_NAME)
                            frameType = CONST_DATA


            if 'command' in status:
                print "command in status"
                if status['command'] == 'ND':

                    print "status['command'] == ND'"

                    # If a node has responded, parse the response to get the mac address
                    # Then, publish to that address inside testbed/gateway/nodes/
                    frameType = CONST_AT
                    if 'parameter' in status:
                        print 'parameter in status'
                        topicStruct = ('testbed/gateway/nodes/')
                        print topicStruct
                        print "publishing data"
                        publish.single(topicStruct, MACtoHex(status,'parameter').encode('hex'), hostname=BROKER_NAME)
                        print "published"
                    # Publish "END" if the last AT command response has been received
                    else:
                        topicStruct = ('testbed/gateway/nodes/')
                        publish.single(topicStruct, "END", hostname=BROKER_NAME)
        except:
            print "an error occured in rxData"
"""

# return list with:
#0: 1 if query, 2 if command, 0 if invalid
#1: index of previous character
def msg_type(msg):
    for i in range(0, len(msg)):
        if msg[i] == '?':
            return [1, i - 1]
        if msg[i] == '=':
            return [2, i - 1]
    return [0, 0]

def on_message(mqttc, obj, msg):
    try:
        global mate3
        print "MQTT MESSAGE RECEIVED"
        # If the received message is a node discover command, send an AT command.
        # If not, it is a data message, and forward it to the xbee.
        
        # the following is no longer applicable:
        #if msg.payload == "NODE_DISCOVER":
            #xbee.at(frame_id='1', command='ND')
        SerNo = msg.topic.split("/")[4]
        print "Serial Number IS:" + SerNo
        #print binascii.unhexlify(SerNo)
        mate3.ser_close()
        mate3.usb_init()
        if mate3.get_serial_number() != SerNo:
            print "Serial Numbers don't match"
            return
        else:
            print "Serial Number match, issuing command"
        mate3.usb_close()
        mate3.ser_init()
        payload = msg.payload

        """
        # If payload is not a properly formed command in hex,
        # convert to hex and make sure the result is terminated with a carriage return. 
        if "\x0A" not in payload:
            print "\\x found in payload. hexlifying: "
            conv = payload.encode("hex") + "0A"
            payload = binascii.unhexlify(conv)

        """

        print "DATA SENT IS:" + payload
        #payload = payload.split('\r')[0]
        
        msg_ti = msg_type(payload)
        print "MSG_TI:", msg_ti
        val_index = payload[msg_ti[1]]
        # get the packet from mate and respond with the appropriate piece of info
        # TODO: figure out what kind of topic structures we need to send to
        if msg_ti[0] == 1:
            print "Attempting to get packet from mate"
            info = mate3.getPacket()
            if payload[:4] == "READ":
                for key in info.keys():
                    for val in range(0, len(info[key])):
                        array = info[key]
                        publishstr = "%s%d=%s" % (key, val, array[val])
                        publish.single("testbed/gateway/data/" + SerNo, publishstr)
                        print "Publishing: ", publishstr
                        sleep (0.01)
                return
            if len(info) == 0:
                print "Invalid packet recieved from mate3"
                return
            #print "STUFF:", ord(val_index)
            if ord(val_index) < 58 and ord(val_index) > 47:
                publishstr = ""
                #for i in range(0, ord(val_index) - 48 + 1): # including the index of the number
                    #publishstr += payload[i]
                templist = info[payload.split(val_index)[0]] # get the list of items for the scenario
                if templist is None:
                    print "Invalid data request: %s" % payload.split(val_index[0])
                    return
                if ord(val_index) - 48 >= len(templist):
                    print "Invalid index %c for %s" % (val_index, payload.split(val_index)[0])
                    return
                publishstr += payload.split(val_index)[0] + val_index + "="
                publishstr += str(templist[ord(val_index) - 48])
                publish.single("testbed/gateway/data/" + SerNo, publishstr)
                print "Publishing: ", publishstr
                print "SENT"
        elif msg_ti[0] == 2:
            print "Not yet ready for commands"
        else:
            print "invalid message type"
        #sleep(1.1)
    except:
        print "An error occurred in on_message"

def Data():
    # for specific client:
    # mqttc = mqtt.Client("client-id")
    print "in Data"
    mqttc = mqtt.Client("mate3Gateway")
    mqttc.on_message = on_message
    mqttc.connect(BROKER_NAME, 1883, 60)
    mqttc.subscribe("testbed/gateway/mqtt/mate3/#", 0)
    mqttc.loop_forever()

# 2 threads:
# rxData has 2 purposes: compile a list of all connected nodes, and pass received data to broker
# txData transmits commands sent by a client.

# rx side no unnecessary
#try:
global mate3
mate3 = Mate3()
mate3.ser_init()
#Thread = threading.Thread(target=Data)
#rxThread = threading.Thread(target=rxData)
#rxThread.start()
#Thread.start()
Data()
    
#except:
print "Problem starting a new thread"
