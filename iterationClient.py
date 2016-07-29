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

nodeList = {}
BROKER_NAME = "127.0.0.1"
# BROKER_NAME = "128.114.63.86"

def on_message(mqttc, obj, msg):
	global nodeList

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
			print "publishing: " + iterList[i] + " MAC ADDRESS: " + i.split(',')[0]
			publish.single("testbed/gateway/mqtt/" + i.split(',')[0], iterList[i], hostname=BROKER_NAME)
			time.sleep(1)

t1 = threading.Thread(target=mqttThread)
t2 = threading.Thread(target=iterationThread)
t1.start()
t2.start()