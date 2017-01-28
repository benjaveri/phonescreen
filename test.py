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
import serial,sys,time
from interfaces import *
from core import *

DBPATH         = ":memory:"
REDIAL_TIMEOUT = 3 #s

class CompletedException(Exception): pass

class FakeModem(Modem):
    def __init__(self):
        self.buf = []
        self.org = time.time()
        self.pgm = [
            # blacklist test
            { "at": 1.0, "from":"408--black", "expect":False },
            # whitelist test
            { "at": 1.5, "from":"408--white", "expect":True },
            # immediate redial test
            { "at": 3.0, "from":"1234567890", "expect":False },
            { "at": 3.1, "from":"1234567890", "expect":True },
            # non-immediate redial test
            { "at": 5.0, "from":"1234567891", "expect":False },
            { "at":10.0, "from":"1234567891", "expect":False },
            # done
            {"at": 15.0, "from": "~" }
        ]

    def emit(self,s):
        #print s
        self.buf.append("OK")

    def readline(self):
        # replay buffered messages
        if len(self.buf):
            front = self.buf[0]
            self.buf = self.buf[1:]
            #print front
            return front

        # pretend to timeout every second (like real modem is set up to do)
        for i in xrange(10):
            # check program for canned messages
            now = time.time() - self.org
            if len(self.pgm) and self.pgm[0]["at"] <= now:
                # terminate when its time
                if self.pgm[0]["from"] == "~":
                    raise CompletedException()

                # play out program
                self.accept = self.pgm[0]["expect"]
                self.buf.append("NMBR = %s" % self.pgm[0]["from"])
                self.buf.append("NAME = test")
                self.pgm = self.pgm[1:]
                return self.readline()

            # else just wait a bit
            time.sleep(0.1)
        return ""

    def accept_call(self):
        assert self.accept

    def reject_call(self,hard):
        assert not self.accept

db = Database(DBPATH)
modem = FakeModem()
core = Core(db,modem,REDIAL_TIMEOUT)
with db as conn:
    conn.execute("INSERT INTO whitelist(number) VALUES (?)",("408--white",))
    conn.execute("INSERT INTO blacklist(number) VALUES (?)",("408--black",))
try:
    core.run()
except CompletedException as e:
    pass
except Exception:
    raise

with db as conn:
  for row in conn.execute("SELECT * FROM WHITELIST"):
    print row
    