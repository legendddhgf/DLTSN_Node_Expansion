#! /usr/bin/python

# Dual threaded implementation of an iteration client:
# one thread will update the nodeList, while the other one iterates through it
# Takes in a command as such:
# topic: "testbed/gateway/mqtt/MACADDRESS"

# Examples:
# message: "START \x23\x14\x12"
# message: "STOP \x13\x42\x12"
# message: "START DH0?"
# message: "STOP T?"

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
import time
import binascii
import argparse

nodeList = {}
BROKER_NAME = "127.0.0.1"
# BROKER_NAME = "128.114.63.86"

def on_message(mqttc, obj, msg):
    global nodeList
    
    device = "Atmega2560"
    tempstr = msg.topic.split("/")[2]
    if tempstr == 'mate3':
        device = "Mate3"
    if device == "Atmega2560":
        mac = msg.topic.split("/")[2]
        condition = msg.payload.split(" ")[0]   
        argument = msg.payload.split(" ")[1]

        # If payload is not a properly formed command in hex,
        # convert to hex and make sure the result is terminated with a carriage return. 
        if "\x0A" not in argument:
            conv = argument.encode("hex") + "0A"
            argument = binascii.unhexlify(conv)

        print "received mac address: " + mac
        if condition == 'START':
            print "starting: " + argument
    
            nodeList[mac + ',' + argument] = argument
        else:
            print "stopping:" + argument
            if (mac + ',' + argument) in nodeList:
                if nodeList[mac + ',' + argument] == argument:
                    del nodeList[mac + ',' + argument]
    elif device == "Mate3":
        SerNo = msg.topic.split("/")[3]
        condition = msg.payload.split(" ")[0]
        argument = msg.payload.split(" ")[1]

        # If payload is not a properly formed command in hex,
        # convert to hex and make sure the result is terminated with a carriage return. 
        if "\x0A" not in argument:
            conv = argument.encode("hex") + "0A"
            argument = binascii.unhexlify(conv)

        print "received serial number: " + SerNo
        if condition == 'START':
            print "starting mate command: " + argument
            nodeList['mate3,' + SerNo + ',' + argument] = argument
        else:
            print "stopping: mate command: " + argument
            if ('mate3,' + SerNo + ',' + argument) in nodeList:
                del nodeList['mate3,' + SerNo + ',' + argument]
    else:
        print "Invalid device error in iteration client"
        exit()

def mqttThread():
    client = mqtt.Client("iterationClient")
    client.on_message = on_message
    client.connect(BROKER_NAME, 1883)
    client.subscribe("testbed/iterationClient/#", 0)
    client.loop_forever()

def iterationThread():
    print "in publishing"
    while(True):
        iterList = nodeList
        # print iterList
        # For each mac address, publish to that mac address
        for i in iterList.keys():
            if i not in iterList:
                continue
            if i.split(',')[0] == 'mate3':
                print "publishing mate3 command: " + iterList[i] + " SERIAL NUMBER: " + i.split(',')[1]
                publish.single("testbed/gateway/mqtt/mate3/" + i.split(',')[1], iterList[i], hostname=BROKER_NAME)
            else:
                print "publishing: " + iterList[i] + " MAC ADDRESS: " + i.split(',')[0]
                publish.single("testbed/gateway/mqtt/" + i.split(',')[0], iterList[i], hostname=BROKER_NAME)
            time.sleep(1)

t1 = threading.Thread(target=mqttThread)
t2 = threading.Thread(target=iterationThread)
t1.start()
t2.start()
