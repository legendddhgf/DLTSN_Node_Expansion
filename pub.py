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

#publish.single("testbed/outback/mate3/0/summary", s, hostname=BROKER_NAME)

#publish.single("testbed/nodeDiscover/command/mate3/", 'START', hostname=BROKER_NAME)

publish.single("testbed/iterationClient/mate3/0000581074", 'STOP BATT_VOLT0?')

publish.single("testbed/iterationClient/mate3/0000581074", 'STOP INV_CUR0?')

publish.single("testbed/iterationClient/12345678", 'STOP L0?')

exit()

ser = serial.Serial("/dev/outback", 19200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, None)

x = {}
zero = 0

s = ""

def m_read():
	x = []
	s = ""
	anothertemp = '\0'
	while (ser.inWaiting() != 0): # flush first
		anothertemp = ser.read()
	sctime = 0.0 # time to get a single character
	iptime = 0.0 # time between beginning and end of packet
	bptime = 0.0 # time between end of packet and beginning of next
	while (zero == 0):# infinite loop
		temp = anothertemp
		if (sctime == 0):
			sctime = time.time() # start counting
			temp = ser.read()
			sctime = time.time() - sctime # now has time for single character
		else:
			temp = ser.read()
		if (ord(temp) == 13):
			bptime = time.time() * (-1) # end of first packet
			break # wait untill beginning of packet
	while (zero == 0): # infinite loop
		x.append(ser.read())
		if (bptime < 0): # called after first byte is read
			bptime += time.time() # one character after start of next packet
			bptime -= sctime # subtract time for single character from previous value
			if bptime < 0:
				bptime = 0
			iptime = time.time() # start of the new packet neglecting a character
		if (ord(x[len(x) - 1]) == 13):
			iptime = time.time() - iptime + sctime # end of the same packet plus time of first character
			break
	for i in range(0, len(x)):
		x[i] = ord(x[i])
	print "Our packet is:\n"
	print x

	chksum = 0	
	desc = ""
	print "\nSize of packet: %d"  % (len(x))
	val = (x[1] - 48) * 10 + (x[2] - 48)
	chksum += (x[1] - 48) + (x[2] - 48)
	print "\nPort Address: %d" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/port_address", s, hostname=BROKER_NAME)
	val = x[4] - 48
	chksum += x[4] - 48
	print "Device type: %d" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/device_type", s, hostname=BROKER_NAME)
	val = (x[6] - 48) * 10 + (x[7] - 48)
	chksum += (x[6] - 48) + (x[7] - 48)
	print "L1 Inverter current: %d [A]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l1_inverter_current", s, hostname=BROKER_NAME)
	val = (x[9] - 48) * 10 + (x[10] - 48)
	chksum += (x[9] - 48) + (x[10] - 48)
	print "L1 Charger current: %d [A]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l1_charger_current", s, hostname=BROKER_NAME)
	val = (x[12] - 48) * 10 + (x[13] - 48)
	chksum += (x[12] - 48) + (x[13] - 48)
	print "L1 Buy current: %d [A]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l1_buy_current", s, hostname=BROKER_NAME)
	val = (x[15] - 48) * 10 + (x[16] - 48)
	chksum += (x[15] - 48) + (x[16] - 48)
	print "L1 Sell current: %d [A]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l1_sell_current", s, hostname=BROKER_NAME)
	val = (x[18] - 48) * 100 + (x[19] - 48) * 10 + (x[20] - 48)
	chksum += (x[18] - 48) + (x[19] - 48) + (x[20] - 48)
	print "L1 Grid input voltage: %d [V]"  % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l1_grid_input_voltage", s, hostname=BROKER_NAME)
	val = (x[22] - 48) * 100 + (x[23] - 48) * 10 + (x[24] - 48)
	chksum += (x[22] - 48) + (x[23] - 48) + (x[24] - 48)
	print "L1 Generator input voltage: %d [V]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l1_generator_input_voltage", s, hostname=BROKER_NAME)
	val = (x[26] - 48) * 100 + (x[27] - 48) * 10 + (x[28] - 48)
	chksum += (x[26] - 48) + (x[27] - 48) + (x[28] - 48)
	print "L1 Output voltage: %d [V]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l1_output_voltage", s, hostname=BROKER_NAME)
	val = (x[30] - 48) * 10 + (x[31] - 48)
	chksum += (x[30] - 48) + (x[31] - 48)
	print "L2 Inverter current: %d [A]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l2_inverter_current", s, hostname=BROKER_NAME)
	val = (x[33] - 48) * 10 + (x[34] - 48)
	chksum += (x[33] - 48) + (x[34] - 48)
	print "L2 Charger current: %d [A]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l2_charger_current", s, hostname=BROKER_NAME)
	val = (x[36] - 48) * 10 + (x[37] - 48)
	chksum += (x[36] - 48) + (x[37] - 48)
	print "L2 Buy current: %d [A]" %  (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l2_buy_current", s, hostname=BROKER_NAME)
	val = (x[39] - 48) * 10 + (x[40] - 48)
	chksum += (x[39] - 48) + (x[40] - 48)
	print "L2 Sell current: %d [A]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l2_sell_current", s, hostname=BROKER_NAME)
	val = (x[42] - 48) * 100 + (x[43] - 48) * 10 + (x[44] - 48)
	chksum += (x[42] - 48) + (x[43] - 48) + (x[44] - 48)
	print "L2 Grid input voltage: %d [V]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l2_grid_input_voltage", s, hostname=BROKER_NAME)
	val = (x[46] - 48) * 100 + (x[47] - 48) * 10 + (x[48] - 48)
	chksum += (x[46] - 48) + (x[47] - 48) + (x[48] - 48)
	print "L2 Generator input voltage: %d [V]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l2_generator_input_voltage", s, hostname=BROKER_NAME)
	val = (x[50] - 48) * 100 + (x[51] - 48) * 10 + (x[52] - 48)
	chksum += (x[50] - 48) + (x[51] - 48) + (x[52] - 48)
	print "L2 Output voltage: %d  [V]" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/l2_output_voltage", s, hostname=BROKER_NAME)
	val = (x[54] - 48) * 10 + (x[55] - 48)
	chksum += (x[54] - 48) + (x[55] - 48)
	if val == 0:
		desc = "Inverter Off"
	elif val == 1:
		desc = "Search"
	elif val == 2:
		desc = "Inverter On"
	elif val == 3:
		desc = "Charge"
	elif val == 4:
		desc = "Silent"
	elif val == 5:
		desc = "Float"
	elif val == 6:
		desc = "Equalize"
	elif val == 7:
		desc = "Charger Off"
	elif val == 8:
		desc = "Support"
	elif val == 9:
		desc = "Sell Enabled"
	elif val == 10:
		desc = "Slave Inverter On"
	elif val == 11:
		desc = "Slave Inverter Off"
	elif val == 12:
		desc = "Offset"
	elif val == 14:
		desc = "Offset"
	elif val == 90:
		desc = "Inverter Error"
	elif val == 91:
		desc = "AGS Error"
	elif val == 92:
		desc == "Comm Error"
	else:
		desc = "Undefined"
	print "Inverter operating mode: %d: %s" % (val, desc)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/inverter_operating_mode", s, hostname=BROKER_NAME)
	val = (x[57] - 48) * 100 + (x[58] - 48) * 10 + (x[59] - 48)
	chksum += (x[57] - 48) + (x[58] - 48) + (x[59] - 48)
	print "Error code: %d" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/error_code", s, hostname=BROKER_NAME)
	print "List of Errors (if empty then no errors):"
	if val & (1 << 0) != 0:
		print "\tLow Vac Output"
	if val & (1 << 1) != 0:
		print "\tStacking Error"
	if val & (1 << 2) != 0:
		print "\tOver Temp"
	if val & (1 << 3) != 0:
		print "\tLow Battery"
	if val & (1 << 4) != 0:
		print "\tComm Fault"
	if val & (1 << 5) != 0:
		print "\tHigh Battery"
	if val & (1 << 6) != 0:
		print "\tShorted Output"
	if val & (1 << 7) != 0:
		print "\tBackfeed"
	print "=========="
	val = (x[61] - 48) * 10 + (x[62] - 48)
	chksum += (x[61] - 48) + (x[62] - 48)
	if val == 0:
		desc = "No AC"
	elif val == 1:
		desc = "AC Drop"
	elif val == 2:
		desc = "AC Use"
	else:
		desc = "Undefined"
	print "AC mode: %d: %s" % (val, desc)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/ac_mode", s, hostname=BROKER_NAME)
	decval = 0.0
	decval = (x[64] - 48) * 100 + (x[65] - 48) * 10 + (x[66] - 48)
	decval /= 10
	chksum += (x[64] - 48) + (x[65] - 48) + (x[66] - 48)
	print "Battery voltage: %.1f [V]" % (decval)
	s = ('%.1f' % decval) + "\r\n"
	publish.single("testbed/outback/mate3/0/battery_voltage", s, hostname=BROKER_NAME)
	val = (x[68] - 48) * 100 + (x[69] - 48) * 10 + (x[70] - 48)
	chksum += (x[68] - 48) + (x[69] - 48) + (x[70] - 48)
	print "Miscellaneous: %d" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/miscellaneous", s, hostname=BROKER_NAME)
	val = (x[72] - 48) * 100 + (x[73] - 48) * 10 + (x[74] - 48)
	chksum += (x[72] - 48) + (x[73] - 48) + (x[74] - 48)
	print "Warning codes: %d" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/warning_codes", s, hostname=BROKER_NAME)
	val = (x[76] - 48) * 100 + (x[77] - 48) * 10 + (x[78] - 48)
	print "Expected Checksum: %d" % (val)
	s = ('%d' % val) + "\r\n"
	publish.single("testbed/outback/mate3/0/expected_checksum", s, hostname=BROKER_NAME)
	print "Calculated Checksum: %d" % chksum
	s = ('%d' % chksum) + "\r\n"
	publish.single("testbed/outback/mate3/0/actual_checksum", s, hostname=BROKER_NAME)

	#print "\nTime for single Character: %f [sec]" % (sctime)
	#print "Time between beginning and end of a single packet: %f [sec]" % (iptime)
	#if bptime < 0:
	#	bptime = 0
	#print "Time between end of one packet and beginning of the next: %f [sec]" % (bptime)

	for i in range(1, 80):
		# print "appending %c" % (chr(x[i]))
		s += chr(x[i])
	s += '\n'

	# print "sending %s" % (s)

	publish.single("testbed/outback/mate3/0/summary", s, hostname=BROKER_NAME)

m_read()

# print "sending %s" % (s)

# publish.single("testbed/iterationClient/0013a20040daebd0", s, hostname=BROKER_NAME)
# publish.single("testbed/iterationClient/0013a20040daebd0", 'STOP L0?', hostname=BROKER_NAME)
# publish.single("testbed/iterationClient/0013a20040a57a9c", 'START \x4C\x30\x3F\x0A', hostname=BROKER_NAME)

# publish.single("testbed/gateway/mqtt/0013a20040daebd0", 'READ', hostname=BROKER_NAME)
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", 'AA0=1', hostname=BROKER_NAME)
# time.sleep(1)
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", 'AA1=1', hostname=BROKER_NAME)
# time.sleep(1)
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", 'AA2=1', hostname=BROKER_NAME)
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", 'READ', hostname=BROKER_NAME)

# publish.single("testbed/gateway/mqtt/0013a20040daebd0", 'READ', hostname=BROKER_NAME)

# publish.single("testbed/gateway/mqtt/" + hexstring, '\x54\x3F\x0A', hostname=BROKER_NAME)

# publish.single("testbed/gateway/mqtt/0013a20040a57a9c", '\x44\x48\x30\x3F\x0A', hostname=BROKER_NAME)

# publish.single("testbed/nodeDiscover/command/", 'START', hostname=BROKER_NAME)

# publish.single("testbed/gateway/mqtt/", 'NODE_DISCOVER', hostname=BROKER_NAME)

# publish.single("testbed/iterationClient/0013a20040a57a9c", 'STOP DH0?', hostname=BROKER_NAME)
# publish.single("testbed/iterationClient/0013a20040a57a9c", 'STOP DT0?', hostname=BROKER_NAME)
# publish.single("testbed/iterationClient/0013a20040a57a9c", 'STOP \x44\x48\x30\x3F\x0A')
# publish.single("testbed/iterationClient/0013a20040daebd0", 'START \x4C\x30\x3F\x0A')
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", 'READ', hostname=BROKER_NAME)
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", '\x52\x45\x41\x44\x0A', hostname=BROKER_NAME)
# AS = "L0", tells the sensor which to base the setpoint off.
# AP = changes the setpoint value.
# AA = "a bool in C. 1 or not 1" Turn on force on (but gets overridden by AO=0)
# AO = on/off, off forces off.
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", 'AP0=3', hostname=BROKER_NAME)

# AO0=1
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", '\x41\x4F\x30\x3D\x31\x0A', hostname=BROKER_NAME)
# AO1=1
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", '\x41\x4F\x31\x3D\x31\x0A', hostname=BROKER_NAME)
# AO2=1
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", '\x41\x4F\x32\x3D\x31\x0A', hostname=BROKER_NAME)

# AP0=50
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", '\x41\x50\x30\x3D\x35\x30\x0A', hostname=BROKER_NAME)
# AP1=100
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", '\x41\x50\x31\x3D\x31\x30\x30\x0A', hostname=BROKER_NAME)
# AP2=400
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", '\x41\x50\x32\x3D\x34\x30\x30\x0A', hostname=BROKER_NAME)

# READ
# publish.single("testbed/gateway/mqtt/0013a20040daebd0", '\x52\x45\x41\x44\x0A', hostname=BROKER_NAME)
