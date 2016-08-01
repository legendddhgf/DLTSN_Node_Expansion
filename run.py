#!/usr/bin/python

from mate_interface import Mate3
import io

zero = 0

mate3 = Mate3()

print "Please enter a command (if you are unsure type \"help\")"
while zero == 0:

    argstr = raw_input("[user @ mate_interface] % ")
    args = argstr.split(' ')
    if len(args) == 0:
        None
        print "Please enter a command (if you are unsure type \"help\")"
    elif args[0] == "help":
        print "Existing commands would be listed and detailed here"
    elif args[0] == "exit":
        break
    elif args[0] == "test1":
        mate3.getPacket()
        #mate3.read()
        #mate3.inv_off()
        mate3.inv_cur()
    elif args[0] == "test2":
        mate3.info()
    elif len(args) > 1 and args[0] == "init" and args[1] == "usb":
        mate3.usb_init()
    elif len(args) > 1 and args[0] == "init" and args[1] == "ser":
        mate3.ser_init()
    elif len(args) > 1 and args[0] == "close" and args[1] == "usb":
        mate3.usb_close()
    elif len(args) > 1 and args[0] == "close" and args[1] == "ser":
        mate3.ser_close()
    else:
        None
        print "Please enter a command (if you are unsure type \"help\")"

print "Have a nice day"
