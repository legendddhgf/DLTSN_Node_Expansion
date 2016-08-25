#! /usr/bin/python

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import serial
BROKER_NAME = "127.0.0.1"
# BROKER_NAME = "128.114.63.86"

hexstring = "0013a20040a57a9c"

# while (True):
# 	publish.single("testbed/scheduler/freq", '60.1', hostname=BROKER_NAME)
# 	time.sleep(5)
# 	publish.single("testbed/scheduler/freq", '59.2', hostname=BROKER_NAME)
# 	time.sleep(5)

s = "SWAGGER"

publish.single("testbed/gateway/data/DEADC0DE", "Battery_volts_av0=14.0")

#publish.single("testbed/nodeDiscover/command/mate3/", 'START', hostname=BROKER_NAME)

#publish.single("testbed/iterationClient/mate3/0000581074", 'START READ?')

#time.sleep(4)

#publish.single("testbed/iterationClient/mate3/0000581074", 'STOP READ?')
"""
publish.single("testbed/iterationClient/midnite-classic/DEADC0DE", 'START READ?')

time.sleep(4)
"""
#publish.single("testbed/iterationClient/midnite-classic/DEADC0DE", 'STOP Battery_volts_av0?')

#publish.single("testbed/iterationClient/mate3/0000581074", 'STOP GRID_IN_VOLT1?')

# publish.single("testbed/iterationClient/12345678", 'STOP L0?')

exit()
