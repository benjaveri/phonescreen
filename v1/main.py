# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import serial,sys,os.path # pip install pyserial
from v1.interfaces import *
from v1.core import *

if len(sys.argv) != 3:
    print "main.py <path for database> <serial port>"
    sys.exit(1)

ECHO = False
PATH = sys.argv[1]
PORT = sys.argv[2]

DBPATH         = os.path.join(PATH,"numbers.sqlite")
REDIAL_TIMEOUT = 60 #s

class RealModem(Modem):
    def __init__(self,port):
        self.ser = serial.Serial(port, 19200, timeout=1)

    def emit(self,s):
        if ECHO: print s
        self.ser.write(s + "\r\n")
        self.ser.flush()

    def readline(self):
        line = self.ser.readline()
        if ECHO: sys.stdout.write(line)
        return line.strip()

    def accept_call(self):
        pass

    def reject_call(self,hard):
        if hard:
            # answer as a fax machine
            #while self.readline() != "RING": time.sleep(0.1)
            self.emit("ATA")
            time.sleep(30)
            #while self.readline() != "CONNECT": time.sleep(0.1)
            self.emit("ATH0")
        else:
            # pick up and hang-up quickly
            self.emit("ATH1")
            time.sleep(.5)
            self.emit("ATH0")


db = Database(DBPATH)
modem = RealModem(PORT)
core = Core(db,modem,REDIAL_TIMEOUT)
core.run()
