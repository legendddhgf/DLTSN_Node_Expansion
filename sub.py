#! /usr/bin/python

# Requirements: mqtt paho library for python installed
import time
import sys
import paho.mqtt.client as mqtt
BROKER_NAME = "128.114.63.86"
BROKER_NAME = "127.0.0.1"
x = 0

def on_message(mqttc, obj, msg):
    print "TOPIC:" + msg.topic
    print "nonhex : " + msg.payload
    global x
    x = x+1
    print x
# for specific client:
# mqttc = mqtt.Client("client-id")


mqttc = mqtt.Client()
mqttc.on_message = on_message

#debug messages
#mqttc.on_log = on_log

mqttc.connect(BROKER_NAME, 1883, 60)
# mqttc.subscribe("testbed/gateway/data/#", 0)
mqttc.subscribe("#", 0)
mqttc.loop_start()
time.sleep(5000)
# mqttc.loop_stop(force=False)
