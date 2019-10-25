# BSD 3-Clause License
#
# Copyright (c) 2017 by Ben de Waal, All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import serial,sys,os.path # pip install pyserial
from interfaces import *
from core import *

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
