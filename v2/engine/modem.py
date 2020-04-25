# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import time, serial # pip install pyserial

NEWLINE = "\r\n"
HEALTH_CHECK_PERIOD = 60*60 # how often to check that modem is still alive

class Modem:
    def poll(self): raise NotImplementedError
    def ring_through(self): raise NotImplementedError
    def answer_as_fax(self, sleep): raise NotImplementedError
    def answer_pulse(self): raise NotImplementedError

#
# this interfaces with real hardware
#
class RealModem(Modem):
    def __init__(self, port):
        self.ser = serial.Serial(port, 19200, timeout=.1)
        self._setup()
        self.next_hc = time.time() + HEALTH_CHECK_PERIOD
        self.buf = ""

    #
    # i/o
    #
    def _emit(self, s):
        self.ser.write((s + NEWLINE).encode("utf-8"))
        self.ser.flush()

    def _readline(self):
        line = self.ser.readline().decode("utf-8")
        if line == NEWLINE:
            return self._readline()
        return line

    #
    # listening operations via polling
    #
    def poll(self):
        # get modem input, if any
        self.buf += self._readline()

        # periodic health check
        if time.time() >= self.next_hc:
            if not self._health_check():
                raise Exception("Modem not responding")
            self.next_hc = time.time() + HEALTH_CHECK_PERIOD

        # parse full lines
        if NEWLINE in self.buf:
            line, self.buf = self.buf.split(NEWLINE,1)
            print("MODEM -> %s" % line)

            # interpret
            if line.startswith("NMBR = "):
                self.num = line[7:]
            elif line.startswith("NAME = "):
                self.name = line[7:]
                return [ self.name, self.num ]

        # nothing to report
        return []

    #
    # modem control
    #
    def _setup(self):
        self._emit("ATZ0")  # reset
        self._emit("ATE0")  # echo off
        self._emit("AT+VCID=1")  # caller-id
        self._emit("AT+FCLASS=0")  # set fax class for hard rejects
        # flush input
        while len(self._readline()): pass

    def _health_check(self):
        self._emit("ATE1")  # echo on
        self._emit("ATE0")  # echo off
        time.sleep(.1)
        return self._readline() == ("OK" + NEWLINE)

    def ring_through(self):
        pass

    def answer_as_fax(self, sleep):
        self._emit("ATA")
        time.sleep(sleep)
        self._emit("ATH0")

    def answer_pulse(self):
        # pick up and hang-up quickly
        self._emit("ATH1")
        time.sleep(.5)
        self._emit("ATH0")


