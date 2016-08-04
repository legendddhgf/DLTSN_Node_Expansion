#!/usr/bin/python

import serial
import io
import time
import usb

zero = 0

class Mate3:

    def __init__(self):
        self.ser_open = False
        self.usb_open = False
        self.dev = usb.core.find() # these two line intend to declare and initalize self.dev
        self.dev = None

    def ser_init(self):
        if self.usb_open:
            print "Please close usb dev before initializing serial"
            return
        self.ser = serial.Serial("/dev/outback", 19200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, 1.05)
        print "Successfully opened /dev/outback self.serial"
        self.ser_open = True

    def ser_close(self):
        if not self.ser_open:
            print "non-open serial interface can't be closed"
            return
        self.ser.close()
        print "Successfully closed serial interface"
        self.ser_open = False

    def usb_init(self):
        if self.ser_open:
            print "Please close serial interface before initializing usb dev"
            return
        self.dev = usb.core.find(idVendor=0x04d8, idProduct=0xf74c)
        if self.dev is not None:
            print "Successfully opened mate usb dev"
            self.usb_open = True
        else:
            print "Device not plugged in"

    def usb_close(self):
        if not self.usb_open:
            print "non-open usb dev can't be closed"
            return
        # self.dev.close() # currently nothing to close unless interface is claimed
        print "Successfully closed mate usb dev"
        self.usb_open = False

    def info(self):
        if not self.usb_open:
            print "Usb device not yet active"
            return
        buf = usb.control.get_descriptor(self.dev, 255, usb.util.DESC_TYPE_STRING, self.dev.iManufacturer)
        str = ""
        for i in range (0, len(buf)):
            str += chr(buf[i])
        print "Manufacturer: ", str

        buf = usb.control.get_descriptor(self.dev, 255, usb.util.DESC_TYPE_STRING, self.dev.iProduct)
        str = ""
        for i in range (0, len(buf)):
            str += chr(buf[i])
        print "Product: ", str

        buf = usb.control.get_descriptor(self.dev, 255, usb.util.DESC_TYPE_STRING, self.dev.iSerialNumber)
        str = ""
        for i in range (0, len(buf)):
            str += chr(buf[i])
        print "Serial Number: ", str

    def get_serial_number(self):
        if not self.usb_open:
            print "Usb device not yet active"
            return
        buf = usb.control.get_descriptor(self.dev, 255, usb.util.DESC_TYPE_STRING, self.dev.iSerialNumber)
        str = ""
        for i in range (0, len(buf)):
            if buf[i] < 58 and buf[i] > 47:
                str += chr(buf[i])
        #print "Giving serial number:", str
        return str

    def getPacket(self):
        x = []
        while (self.ser.inWaiting() != 0): # flush first
            self.ser.read()
        sctime = 0.0 # time to get a single character
        iptime = 0.0 # time between beginning and end of packet
        bptime = 0.0 # time between end of packet and beginning of next
        '''
        while (zero == 0):# infinite loop
            temp = '\0'
            if (sctime == 0):
                sctime = time.time() # start counting
                temp = self.ser.read()
                sctime = time.time() - sctime # now has time for single character
            else:
                temp = self.ser.read()
            if (ord(temp) == 13):
                bptime = time.time() * (-1) # end of first packet
                break # wait untill beginning of packet
        '''
        while (zero == 0): # infinite loop
            x.append(self.ser.read())
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
        #print "Our packet is:\n"
        #print x

        if len(x) != 80:
            return {}

        packet = {}
    
        chksum = 0  
        desc = ""
        #print "\nSize of packet: %d"  % (len(x))
        val = (x[1] - 48) * 10 + (x[2] - 48)
        chksum += (x[1] - 48) + (x[2] - 48)
        #print "\nPort Address: %d" % (val)
        packet['PORT_ADDR'] = []
        packet['PORT_ADDR'].append(val)
        val = x[4] - 48
        chksum += x[4] - 48
        #print "Device type: %d" % (val)
        packet['DEV_TYPE'] = []
        packet['DEV_TYPE'].append(val)
        val = (x[6] - 48) * 10 + (x[7] - 48)
        chksum += (x[6] - 48) + (x[7] - 48)
        #print "L1 Inverter current: %d [A]" % (val)
        packet['INV_CUR'] = []
        packet['INV_CUR'].append(val)
        val = (x[9] - 48) * 10 + (x[10] - 48)
        chksum += (x[9] - 48) + (x[10] - 48)
        #print "L1 Charger current: %d [A]" % (val)
        packet['CHG_CUR'] = []
        packet['CHG_CUR'].append(val)
        val = (x[12] - 48) * 10 + (x[13] - 48)
        chksum += (x[12] - 48) + (x[13] - 48)
        #print "L1 Buy current: %d [A]" % (val)
        packet['BUY_CUR'] = []
        packet['BUY_CUR'].append(val)
        val = (x[15] - 48) * 10 + (x[16] - 48)
        chksum += (x[15] - 48) + (x[16] - 48)
        #print "L1 Sell current: %d [A]" % (val)
        packet['SELL_CUR'] = []
        packet['SELL_CUR'].append(val)
        val = (x[18] - 48) * 100 + (x[19] - 48) * 10 + (x[20] - 48)
        chksum += (x[18] - 48) + (x[19] - 48) + (x[20] - 48)
        #print "L1 Grid input voltage: %d [V]"  % (val)
        packet['GRID_IN_VOLT'] = []
        packet['GRID_IN_VOLT'].append(val)
        val = (x[22] - 48) * 100 + (x[23] - 48) * 10 + (x[24] - 48)
        chksum += (x[22] - 48) + (x[23] - 48) + (x[24] - 48)
        #print "L1 Generator input voltage: %d [V]" % (val)
        packet['GEN_IN_VOLT'] = []
        packet['GEN_IN_VOLT'].append(val)
        val = (x[26] - 48) * 100 + (x[27] - 48) * 10 + (x[28] - 48)
        chksum += (x[26] - 48) + (x[27] - 48) + (x[28] - 48)
        #print "L1 Output voltage: %d [V]" % (val)
        packet['OUT_VOLT'] = []
        packet['OUT_VOLT'].append(val)
        val = (x[30] - 48) * 10 + (x[31] - 48)
        chksum += (x[30] - 48) + (x[31] - 48)
        #print "L2 Inverter current: %d [A]" % (val)
        packet['INV_CUR'].append(val)
        val = (x[33] - 48) * 10 + (x[34] - 48)
        chksum += (x[33] - 48) + (x[34] - 48)
        #print "L2 Charger current: %d [A]" % (val)
        packet['CHG_CUR'].append(val)
        val = (x[36] - 48) * 10 + (x[37] - 48)
        chksum += (x[36] - 48) + (x[37] - 48)
        #print "L2 Buy current: %d [A]" %  (val)
        packet['BUY_CUR'].append(val)
        val = (x[39] - 48) * 10 + (x[40] - 48)
        chksum += (x[39] - 48) + (x[40] - 48)
        #print "L2 Sell current: %d [A]" % (val)
        packet['SELL_CUR'].append(val)
        val = (x[42] - 48) * 100 + (x[43] - 48) * 10 + (x[44] - 48)
        chksum += (x[42] - 48) + (x[43] - 48) + (x[44] - 48)
        #print "L2 Grid input voltage: %d [V]" % (val)
        packet['GRID_IN_VOLT'].append(val)
        val = (x[46] - 48) * 100 + (x[47] - 48) * 10 + (x[48] - 48)
        chksum += (x[46] - 48) + (x[47] - 48) + (x[48] - 48)
        #print "L2 Generator input voltage: %d [V]" % (val)
        packet['GEN_IN_VOLT'].append(val)
        val = (x[50] - 48) * 100 + (x[51] - 48) * 10 + (x[52] - 48)
        chksum += (x[50] - 48) + (x[51] - 48) + (x[52] - 48)
        #print "L2 Output voltage: %d  [V]" % (val)
        packet['OUT_VOLT'].append(val)
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
        #print "Inverter operating mode: %d: %s" % (val, desc)
        packet['INV_OP_MODE'] = []
        packet['INV_OP_MODE'].append(val)
        val = (x[57] - 48) * 100 + (x[58] - 48) * 10 + (x[59] - 48)
        chksum += (x[57] - 48) + (x[58] - 48) + (x[59] - 48)
        #print "Error code: %d" % (val)
        packet['ERROR_CODE'] = []
        packet['ERROR_CODE'].append(val)
        #print "List of Errors (if empty then no errors):"
        '''
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
        '''
        #print "=========="
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
        #print "AC mode: %d: %s" % (val, desc)
        packet['AC_MODE'] = []
        packet['AC_MODE'].append(val)
        decval = 0.0
        decval = (x[64] - 48) * 100 + (x[65] - 48) * 10 + (x[66] - 48)
        decval /= 10
        chksum += (x[64] - 48) + (x[65] - 48) + (x[66] - 48)
        #print "Battery voltage: %.1f [V]" % (decval)
        packet['BATT_VOLT'] = []
        packet['BATT_VOLT'].append(decval * 10)
        val = (x[68] - 48) * 100 + (x[69] - 48) * 10 + (x[70] - 48)
        chksum += (x[68] - 48) + (x[69] - 48) + (x[70] - 48)
        #print "Miscellaneous: %d" % (val)
        packet['MISC'] = []
        packet['MISC'].append(val)
        val = (x[72] - 48) * 100 + (x[73] - 48) * 10 + (x[74] - 48)
        chksum += (x[72] - 48) + (x[73] - 48) + (x[74] - 48)
        #print "Warning codes: %d" % (val)
        packet['WARN_CODE'] = []
        packet['WARN_CODE'].append(val)
        val = (x[76] - 48) * 100 + (x[77] - 48) * 10 + (x[78] - 48)
        #print "Expected Checksum: %d" % (val)
        packet['EXP_CHKSM'] = []
        packet['EXP_CHKSM'].append(val)
        #print "Calculated Checksum: %d" % chksum
        packet['CALC_CHKSM'] = []
        packet['CALC_CHKSM'].append(val)

        #print "The returned packet will be:"
        #print packet
        return packet


    # from this point on we need verification that we have either usb interface or serial interface
    def read(self):
        x = []
        while (self.ser.inWaiting() != 0): # flush first
            self.ser.read()
        sctime = 0.0 # time to get a single character
        iptime = 0.0 # time between beginning and end of packet
        bptime = 0.0 # time between end of packet and beginning of next
        while (zero == 0):# infinite loop
            temp = '\0'
            if (sctime == 0):
                sctime = time.time() # start counting
                temp = self.ser.read()
                sctime = time.time() - sctime # now has time for single character
            else:
                temp = self.ser.read()
            if (ord(temp) == 13):
                bptime = time.time() * (-1) # end of first packet
                break # wait untill beginning of packet
        while (zero == 0): # infinite loop
            x.append(self.ser.read())
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

        if len(x) != 80:
            return
    
        chksum = 0  
        desc = ""
        print "\nSize of packet: %d"  % (len(x))
        val = (x[1] - 48) * 10 + (x[2] - 48)
        chksum += (x[1] - 48) + (x[2] - 48)
        print "\nPort Address: %d" % (val)
        val = x[4] - 48
        chksum += x[4] - 48
        print "Device type: %d" % (val)
        val = (x[6] - 48) * 10 + (x[7] - 48)
        chksum += (x[6] - 48) + (x[7] - 48)
        print "L1 Inverter current: %d [A]" % (val)
        val = (x[9] - 48) * 10 + (x[10] - 48)
        chksum += (x[9] - 48) + (x[10] - 48)
        print "L1 Charger current: %d [A]" % (val)
        val = (x[12] - 48) * 10 + (x[13] - 48)
        chksum += (x[12] - 48) + (x[13] - 48)
        print "L1 Buy current: %d [A]" % (val)
        val = (x[15] - 48) * 10 + (x[16] - 48)
        chksum += (x[15] - 48) + (x[16] - 48)
        print "L1 Sell current: %d [A]" % (val)
        val = (x[18] - 48) * 100 + (x[19] - 48) * 10 + (x[20] - 48)
        chksum += (x[18] - 48) + (x[19] - 48) + (x[20] - 48)
        print "L1 Grid input voltage: %d [V]"  % (val)
        val = (x[22] - 48) * 100 + (x[23] - 48) * 10 + (x[24] - 48)
        chksum += (x[22] - 48) + (x[23] - 48) + (x[24] - 48)
        print "L1 Generator input voltage: %d [V]" % (val)
        val = (x[26] - 48) * 100 + (x[27] - 48) * 10 + (x[28] - 48)
        chksum += (x[26] - 48) + (x[27] - 48) + (x[28] - 48)
        print "L1 Output voltage: %d [V]" % (val)
        val = (x[30] - 48) * 10 + (x[31] - 48)
        chksum += (x[30] - 48) + (x[31] - 48)
        print "L2 Inverter current: %d [A]" % (val)
        val = (x[33] - 48) * 10 + (x[34] - 48)
        chksum += (x[33] - 48) + (x[34] - 48)
        print "L2 Charger current: %d [A]" % (val)
        val = (x[36] - 48) * 10 + (x[37] - 48)
        chksum += (x[36] - 48) + (x[37] - 48)
        print "L2 Buy current: %d [A]" %  (val)
        val = (x[39] - 48) * 10 + (x[40] - 48)
        chksum += (x[39] - 48) + (x[40] - 48)
        print "L2 Sell current: %d [A]" % (val)
        val = (x[42] - 48) * 100 + (x[43] - 48) * 10 + (x[44] - 48)
        chksum += (x[42] - 48) + (x[43] - 48) + (x[44] - 48)
        print "L2 Grid input voltage: %d [V]" % (val)
        val = (x[46] - 48) * 100 + (x[47] - 48) * 10 + (x[48] - 48)
        chksum += (x[46] - 48) + (x[47] - 48) + (x[48] - 48)
        print "L2 Generator input voltage: %d [V]" % (val)
        val = (x[50] - 48) * 100 + (x[51] - 48) * 10 + (x[52] - 48)
        chksum += (x[50] - 48) + (x[51] - 48) + (x[52] - 48)
        print "L2 Output voltage: %d  [V]" % (val)
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
        val = (x[57] - 48) * 100 + (x[58] - 48) * 10 + (x[59] - 48)
        chksum += (x[57] - 48) + (x[58] - 48) + (x[59] - 48)
        print "Error code: %d" % (val)
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
        decval = 0.0
        decval = (x[64] - 48) * 100 + (x[65] - 48) * 10 + (x[66] - 48)
        decval /= 10
        chksum += (x[64] - 48) + (x[65] - 48) + (x[66] - 48)
        print "Battery voltage: %.1f [V]" % (decval)
        val = (x[68] - 48) * 100 + (x[69] - 48) * 10 + (x[70] - 48)
        chksum += (x[68] - 48) + (x[69] - 48) + (x[70] - 48)
        print "Miscellaneous: %d" % (val)
        val = (x[72] - 48) * 100 + (x[73] - 48) * 10 + (x[74] - 48)
        chksum += (x[72] - 48) + (x[73] - 48) + (x[74] - 48)
        print "Warning codes: %d" % (val)
        val = (x[76] - 48) * 100 + (x[77] - 48) * 10 + (x[78] - 48)
        print "Expected Checksum: %d" % (val)
        print "Calculated Checksum: %d" % chksum
    
        #print "\nTime for single Character: %f [sec]" % (sctime)
        #print "Time between beginning and end of a single packet: %f [sec]" % (iptime)
        #if bptime < 0:
        #   bptime = 0
        #print "Time between end of one packet and beginning of the next: %f [sec]" % (bptime)
    
    def packetcount(self, sec = 10):
        while (zero == 0):
            while (self.ser.inWaiting() != 0): # flush first
                self.ser.read()
            temp = self.ser.read()
            if (ord(temp) == 13):
                break
        timestart = time.time() # beginning of 10 second polling period
        numpacketxsec = 0 # number of packets in 10 second period
        asctime = 0.0 # average time for first character of packet to be recieved
        aiptime = 0.0 # average time for an entire packet to be sent
        abptime = 0.0 # average time between the end of a packet and the start of the next
        temp1 = 0.0 # used for asctime
        temp2 = 0.0 # used for aiptime
        temp3 = time.time() # used for abptime, end of current packet
        while(zero == 0):
            
            if temp1 == 0: # first character
                while self.ser.inWaiting() == 0:
                    # busy wait
                    None
                temptime = time.time()
                abptime += temptime - temp3 # add time to beginning of next packet
                print "\nRuntime: %f" % (time.time() - timestart)
                print "\nTime between end of packet and beginning of next %d: %f" % (numpacketxsec + 1, temptime - temp3)
                temp1 = temptime
                temp2 = temptime
                temp = self.ser.read()
                temptime = time.time()
                print "\nRuntime: %f" % (time.time() - timestart)
                print "\nCharacter recieve time %d: %f" % (numpacketxsec + 1, temptime - temp1)
                asctime += temptime - temp1 # add time of character recieve
            else:
                temp = self.ser.read()
            if (ord(temp) == 13):
                temptime = time.time()
                numpacketxsec += 1
                aiptime += temptime - temp2 # add time to end of packet
                print "\nRuntime: %f" % (time.time() - timestart)
                print "\nTime from beginning to end of packet %d: %f" % (numpacketxsec, temptime - temp2)
                temp1 = 0.0 # clear temp1 to be read next time
                temp2 = 0.0 # clear temp2 but not necessary now
                temp3 = temptime # end of packet
                if (temptime - timestart >= sec):
                    break
        timeend = time.time()
    
        asctime /= numpacketxsec
        aiptime /= numpacketxsec
        abptime /= numpacketxsec
    
        print "\nNumber of packets recieved in %f seconds: %d" % ((timeend - timestart), numpacketxsec)
        print "Average time per first character recieve over %d packets: %f" % (numpacketxsec, asctime)
        print "Average time from beginning to end of packet over %d packets: %f" % (numpacketxsec, aiptime)
        print "Average time end of packet to beginning of next over %d packets: %f" % (numpacketxsec, abptime)
    
    def cspeedtest(self, sec = 10): # test recieve time for all characters
    
        while (self.ser.Inwaiting() != 0): # flush first
            self.ser.read()
        start = time.time()
        while zero == 0:
            if time.time() - start >= sec:
                break
            temp = time.time()
            tempc = self.ser.read()
            print "Character with value %d took %f seconds to be read" % (ord(tempc), time.time() - temp)
            if ord(tempc) == 13:
                print ""
                while self.ser.inWaiting() == 0:
                    None    
    
    def inv_off(self):
        s = '<INV:0>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)

    def inv_search(self):
        s = '<INV:1>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)


    def inv_on(self):
        s = '<INV:2>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def inv_cur(self):
        s = '<INV:?>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def firmware(self):
        s = '<FIRM3:?>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def bat_temp(self):
        s = '<BTEMP:?>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def inv_temp(self):
        s = '<TEMP:p>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def inv_chg_off(self):
        s = '<CHG:0>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def inv_chg_on(self):
        s = '<CHG:2>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def inv_chg_cur(self):
        s = '<CHG:?>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def ac_drop(self):
        s = '<AC:0>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def ac_use(self):
        s = '<AC:1>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def ac_cur(self):
        s = '<AC:?>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def gen_off(self):
        s = '<GEN:0>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)
    
    def gen_on(self):
        s = '<GEN:1>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)

    def gen_auto(self):
        s = '<GEN:2>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)

    def gen_cur(self):
        s = '<GEN:?>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)

    def inv_sell_dis(self):
        s = '<SELL:0>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)

    def inv_sell_en(self):
        s = '<SELL:1>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)

    def inv_sell_cur(self):
        s = '<SELL:?>'
        nb = self.ser.write(s)
        if nb == len(s):
            print "successfully wrote string"
        else:
            print "write unsuccessful"
        print "Note: s is size (%s) and number of bytes processed (%s)\n" % (len(s), nb)
        while self.ser.read() != '[': # beginning of response
            None
        s = '['
        while s[len(s) - 1] != ']':
            s += self.ser.read()
        print "Return is %s\n" % (s)


