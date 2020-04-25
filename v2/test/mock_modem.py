# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
from engine.modem import Modem
import time

#
# this modem lets us do unit testing
#
class CompletedException(Exception): pass

class MockModem(Modem):
    def __init__(self, prog):
        self.org = time.time()
        self.prog = prog

    def poll(self):
        # play back programmed modem commands
        now = time.time() - self.org
        if len(self.prog) and self.prog[0]["at"] <= now:
            # terminate when its time
            if self.prog[0]["from"] is None:
                raise CompletedException()

            # play out next step in program
            self.expected = self.prog[0]["expect"]
            num = self.prog[0]["from"]
            self.prog = self.prog[1:]
            print("**********************************************")
            print("AT %f RING %s EXPECT %s" % (now, num, self.expected))
            return [ "test", num ]

        # nothing to report
        return []

    def ring_through(self):
        assert self.expected == "accept"

    def answer_as_fax(self, sleep):
        assert self.expected == "block"

    def answer_pulse(self):
        assert self.expected == "pulse"

