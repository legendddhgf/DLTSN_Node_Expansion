#! /usr/bin/python

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
import time
import argparse
from mate_interface import Mate3

def cut_non_digits(x):
    str = ""
    if type(x) != type(str):
        print "cut_zeros() accepts only strings"
        exit()
    for i in range(0, len(x)):
        if ord(x[i]) > 47 and ord(x[i]) < 58:
            str += x[i]
    return str

BROKER_NAME = "127.0.0.1"
# BROKER_NAME = "128.114.63.86"

GET_TYPE = '\x49\x3F\x0A'
# GET_TYPE = '\x52\x45\x41\x44\x0A'
# DATA POINT: GET_TYPE = '\x44\x48\x30\x3F\x0A'
NODE_DISCOVER_WAIT_DURATION = 5

SEND_ND = 0
state2Counter = 0
State = 1
nodeList = {}
# publish.single("testbed/gateway/mqtt/" + hexstring, '\x54\x3F\x0A', hostname=BROKER_NAME)


# State 1 runs AT command ND, and collects it all into a global nodeList[] python dictionary.

# It has 3 functions:
# on_connect_state1() will send a node discover command to the gateway 
# when the client is connected to the broker.
# As loop_start() automatically handles reconnection to the broker in case
# of a random unexpected disconnect, a global SEND_ND is used as a check
# to assure node discover message is published only once per run. 

# on_message_state() loops until one of two occurrences: 
#  1. Xbees automatically send a termination message at the end of node discover
#     This is parsed automatically by the gateway, and comes in the form of "END"
#  2. Timeout, set by NODE_DISCOVER_WAIT_DURATION

# state1() starts the thread running on_connect_state1 and on_message_state1
# and manages the mqtt client. 
# It also resets the SEND_ND variable used by on_connect_state1(), and 
# can break out of the on_connect_state1 and on_message_state1 threads upon timeout

# Publish a command when the client connects
def on_connect_state1(client, userdata, rc):
    global SEND_ND
    global device
    # Only send a node discover the first time on_message1 is called.
    if SEND_ND == 0:
        if device == 'Atmega2560':
            publish.single("testbed/gateway/mqtt/", 'NODE_DISCOVER', hostname=BROKER_NAME)
        elif device == 'Mate3':
            publish.single("testbed/gateway/mqtt/", 'NODE_DISCOVER_MATE3', hostname=BROKER_NAME)
        else:
            print "Invalid device name: %s" % device
            exit()
        SEND_ND = 1

# TODO: please make this work with Mate3 device
def on_message_state1(client1, obj, msg):
    global State
    global nodeList
    print "In state1 On Message"
    print "message received: " + msg.payload

    # If a received message isn't the end
    # Make an empty dictionary entry for the received message
    # mapping the mac address of an xbee to a dictionary.
    if msg.payload != "END":
        nodeList[msg.payload] = None
    else:
        print "Ending State 1 of Node Discovery"
        State = 2
        # client1.loop_stop(force=False)

def state1():
    global SEND_ND
    global State
    global device
    SEND_ND = 0
    print "In State 1:"
    clientstr = "str"
    if device == 'Atmega2560': # string depends on device
        clientstr = "xbeeNodeDiscoverS1"
    elif device == 'Mate3':
        clientstr = "mate3NodeDiscovers1"
    # else:
        # print "Invalid device specified: %s" % device
        # exit()
    client1 = mqtt.Client(clientstr)
    client1.on_message = on_message_state1
    
    # starts sending messages on connect -- appears to be fast enough to catch all messages.
    client1.connect(BROKER_NAME, 1883, NODE_DISCOVER_WAIT_DURATION)
    client1.subscribe("testbed/gateway/nodes/", 0)
    client1.on_connect = on_connect_state1
    print "starting on_message_state 1:"
    if State == 1:
        client1.loop_start()
    time.sleep(NODE_DISCOVER_WAIT_DURATION)
    # guarantee the loop has stopped
    client1.loop_stop(force=False)

# state2 takes nodeList[] from state1, queries each address in nodeList[] and sends a message
# to the gateway, which then returns the types of devices associated with each MAC address

# State2 has 3 functions: on_connect_state2(), on_message_state2(), and state2().
# on_connect_state2() runs as soon as the client connects, and for each MAC address in nodeList,
# publishes GET_TYPE requests to the broker.
# even though on_connect_state2() has the possibility of running more than once
# as loop_start() handles reconnection to broker, a check is implemented in
# on_message_state2() that handles this.

# on_message_state2() waits for messages from the broker and checks received messages
# if the address of the sender matches with an entry on nodeList, and if the received
# message is unique.
def on_connect_state2(client2, userdata, rc):
    global nodeList
    # global state2Counter
    print "In state2 on connect message"
    for MacAddr in nodeList:
        print MacAddr
        publish.single("testbed/gateway/mqtt/" + MacAddr, GET_TYPE, hostname=BROKER_NAME)
        # Increment state2counter so on_message_state2 knows when to stop searching
        # state2Counter = state2Counter + 1
    # Disconnect after messages are sent


# Uses nodeList[] for a list of nodes to send a query command to, and wait for response
def on_message_state2(client, obj, msg):
    global State
    global nodeList
    global state2Counter
    print "IN ON_MESSAGE_STATE"
    if State == 0:
        client.loop_stop(force=False)
        return
    # msg.topic.split will eventually return the mac address.
    # when this is implemented, we can set nodeList[msg.topic.split("/"[-1])] = queried data.
    MACfromTopic = msg.topic.split("/")[-1]
    if MACfromTopic not in nodeList:
        State = 0
        print "ATTEMPTING TO ADD A NON-ELEMENT OF nodeList"
        client.loop_stop(force=False)
        return
    
    # Only update nodeList[MACfromTopicc] and state2Counter if unique MAC address
    if state2Counter < (len(nodeList)):
        if nodeList[MACfromTopic] != msg.payload:
            nodeList[MACfromTopic] = msg.payload
            state2Counter = state2Counter + 1


    nodeList[MACfromTopic] = msg.payload
    print nodeList
    print "Reached end of on_message_state2"

def state2():
    global state2Counter
    global nodeList

    state2Counter = 0
    print "IN receive_state2"

    client2 = mqtt.Client("xbeeNodeDiscoverS2send")
    client2.connect(BROKER_NAME, 1883, NODE_DISCOVER_WAIT_DURATION)
    client2.on_connect = on_connect_state2
    

    client = mqtt.Client("xbeeNodeDiscoverS2receive")
    client.connect(BROKER_NAME, 1883, 60)
    client.subscribe("testbed/nodeDiscover/data/#", 0)
    client.on_message = on_message_state2
    
    client2.loop_start()
    client.loop_start()

    time.sleep(NODE_DISCOVER_WAIT_DURATION)
    client.loop_stop(force=False)
    client2.loop_stop(force=False)
    print "receive_state2() ending"
# 2 threads so can break out of scanning if nothing is found after a certain duration of time
# client.loop(timeout=X) doesn't work


# Node discover is done in 2 states: collecting mac addresses, and querying each one.
# A 3rd state rearms nodeDiscover to allow it to iterate again.
# on_message() serves main(), and starts 

def on_message(client, obj, msg):
    print "Command received by nodeDiscover Client"
    if msg.payload == "START":
        print "Starting node discovery..."

        # State1 will loop until it disconnects, and will be followed by state2, which does the same
        state1()
        state2()
        print "-------END OF STATE 1 AND 2-------"
        print nodeList
        main()

# This part runs first.
# to start it, send message "START" to testbed/nodeDiscover/

# on_connect() is defined here just in case, to override the on_connect 
# of other functions
def on_connect(client,obj,msg):
    pass

def mate3_on_message(client,obj,msg):
    print "Command received by nodeDiscover Client"
    if msg.payload != "START":
        return
    print "Starting Mate3 node discovery..."
    mate3 = Mate3()
    mate3.usb_init()
    SerNo = cut_non_digits(mate3.get_serial_number())
    sendstr = 'PORT_ADDR=1'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'DEV_TYPE=1'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'INV_CUR=2'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'CHG_CUR=2'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'BUY_CUR=2'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'SELL_CUR=2'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'GRID_IN_VOLT=2'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'GEN_IN_VOLT=2'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'OUT_VOLT=2'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'INV_OP_MODE=1'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'ERROR_CODE=1'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'AC_MODE=1'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'BATT_VOLT=1'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'MISC=1'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'WARN_CODE=1'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    sendstr = 'VALID_CHKSM=1'
    publish.single("testbed/nodeDiscover/data/mate3/" + str(SerNo), sendstr, hostname=BROKER_NAME)
    print "Mate3 node discovery complete"
    exit()

def main():
    print "\n--IN MAIN--\n"
    # Set/reset all variables and states
    global SEND_ND
    global state2Counter
    global State
    global nodeList
    global single_run
    global device

    # have options for specifying device (like looking for a mate3 over usb instead of an arduino over xbee)
    clientstr = ""
    if device == 'Atmega2560':
        clientstr = "xbeeNodeDiscover"
    elif device == 'Mate3':
        client = mqtt.Client(clientstr)
        client.on_message = mate3_on_message
        client.on_connect = on_connect
        client.connect(BROKER_NAME, 1883)
        client.subscribe("testbed/nodeDiscover/command/", 0)
        client.loop_forever()
        return

    SEND_ND = 0
    state2Counter = 0
    State = 1
    nodeList.clear()

    client = mqtt.Client(clientstr)
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(BROKER_NAME, 1883)
    client.subscribe("testbed/nodeDiscover/command/", 0)
    client.loop_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse options for running nodeDiscover')
    parser.add_argument('-sr', '--single_run', type=str, choices=['yes'], help='Make node discover run once instead of infinitely loop.')
    parser.add_argument('-d', '--device', type=str, choices=['Mate3'], help='Specify a device to run nodeDiscover on.')
    args = parser.parse_args()
    global single_run
    global device
    device = 'Atmega2560'
    single_run = False
    '''
    if args.single_run == 'yes':
        single_run = True
        print "single_run=%r" % single_run
    else:
        single_run = False
        print "single_run=%r" % single_run
    '''
    if args.device == None:
        print 'device=Atmega2560'
    else:
        device = args.device
        print "device=%s" % device
    main()
