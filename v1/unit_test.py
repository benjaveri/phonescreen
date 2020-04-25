# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
from v1.interfaces import *
from v1.core import *

DBPATH         = ":memory:"
REDIAL_TIMEOUT = 3 #s

class CompletedException(Exception): pass

class FakeModem(Modem):
    def __init__(self):
        self.buf = []
        self.org = time.time()
        self.pgm = [
            # blacklist test
            { "at": 1.0, "from":"408--black", "expect":"hard-reject" },
            # whitelist test
            { "at": 1.5, "from":"408--white", "expect":"accept" },
            # immediate redial test
            { "at": 3.0, "from":"1234567890", "expect":"soft-reject" },
            { "at": 3.1, "from":"1234567890", "expect":"accept" },
            # non-immediate redial test
            { "at": 5.0, "from":"1234567891", "expect":"soft-reject" },
            { "at":10.0, "from":"1234567891", "expect":"soft-reject" },
            # blacklist promotion
            {"at": 15.0, "from": "1234567891", "expect": "soft-reject"},
            {"at": 20.0, "from": "1234567891", "expect": "soft-reject"},
            {"at": 25.0, "from": "1234567891", "expect": "soft-reject"},
            {"at": 30.0, "from": "1234567891", "expect": "hard-reject"},
            # done
            {"at": 35.0, "from": "~" }
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
                self.expected = self.pgm[0]["expect"]
                self.buf.append("NMBR = %s" % self.pgm[0]["from"])
                self.buf.append("NAME = test")
                self.pgm = self.pgm[1:]
                return self.readline()

            # else just wait a bit
            time.sleep(0.1)
        return ""

    def accept_call(self):
        assert self.expected == "accept"

    def reject_call(self,hard):
        assert self.expected == ("hard-reject" if hard else "soft-reject")

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

print "WHITELIST"
with db as conn:
  for row in conn.execute("SELECT * FROM whitelist"):
    print row

print "BLACKLIST"
with db as conn:
  for row in conn.execute("SELECT * FROM blacklist"):
    print row
