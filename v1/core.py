# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import time

class Core:
    def __init__(self,db,modem,redial_timeout):
        self.db = db
        self.modem = modem
        self.redial_timeout = redial_timeout

        with self.db as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS props (id INTEGER PRIMARY KEY ASC,key TEXT UNIQUE,value TEXT)")

            conn.execute("CREATE TABLE IF NOT EXISTS whitelist (id INTEGER PRIMARY KEY ASC,number TEXT UNIQUE)")
            conn.execute("CREATE INDEX IF NOT EXISTS whitelistNumberIndex ON whitelist (number ASC)")

            conn.execute("CREATE TABLE IF NOT EXISTS blacklist (id INTEGER PRIMARY KEY ASC,number TEXT UNIQUE)")
            conn.execute("CREATE INDEX IF NOT EXISTS blacklistNumberIndex ON blacklist (number ASC)")

            conn.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY ASC,epoch INTEGER,number TEXT,name TEXT)")
            conn.execute("CREATE INDEX IF NOT EXISTS historyEpochIndex ON history (epoch ASC)")

    def run(self):
        data = {}

        def reset():
            data = {}

        def expect(ref):
            line = ""
            while not(len(line)): line = self.modem.readline()
            assert line == ref

        #
        # set up modem
        #
        self.modem.emit("ATZ0") # reset
        self.modem.emit("ATE0") # echo off
        while len(self.modem.readline()): pass
        self.modem.emit("AT+VCID=1") # caller-id
        self.modem.emit("AT+FCLASS=0") # set fax class for hard rejects

        reset()
        while True:
            line = self.modem.readline()

            if line.startswith("DATE = "): data["date"] = line[7:]
            elif line.startswith("TIME = "): data["time"] = line[7:]
            elif line.startswith("NMBR = "): data["nmbr"] = line[7:]
            elif line.startswith("NAME = "):
                data["name"] = line[7:]

                with self.db as conn:
                    number = data["nmbr"]
                    name = data["name"]
                    now = time.time()

                    accept = False
                    for row in conn.execute("SELECT number FROM whitelist WHERE number=?",(number,)):
                        accept = True

                    reject = False
                    for row in conn.execute("SELECT number FROM blacklist WHERE number=?",(number,)):
                        reject = True

                    if reject:
                        print "Hard rejecting blacklisted %s (%s)" % (number,name)
                        self.modem.reject_call(True)
                    elif accept:
                        print "Accepting whitelisted %s (%s)" % (number,name)
                        self.modem.accept_call()
                    else:
                        accept = False
                        for row in conn.execute("SELECT epoch FROM history WHERE number=?",(number,)):
                            diff = now - int(row[0])
                            if diff <= self.redial_timeout:
                                accept = True
                                break
                        
                        if accept:
                            print "Auto whitelisting and accepting %s (%s)" % (number,name)
                            conn.execute("INSERT OR REPLACE INTO whitelist(number) VALUES (?)",(number,))
                            self.modem.accept_call()
                        else:
                            print "Soft rejecting unknown %s (%s)" % (number,name)
                            self.modem.reject_call(False)
                            # check if we have rejected this call 4 times before - if so, promote to black list
                            for row in conn.execute("SELECT COUNT(*) FROM history WHERE number=?",(number,)):
                                if int(row[0]) >= 4:
                                    conn.execute("INSERT OR REPLACE INTO blacklist(NUMBER) VALUES (?)",(number,))

                    # update call history
                    conn.execute("INSERT INTO history(epoch,number,name) VALUES (?,?,?)",(now,number,name))

                # reset data for next call
                reset()
