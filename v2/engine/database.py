# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import sqlite3, time

# log states
LS_IDLE  = "idle"
LS_BLOCK = "blacklist"
LS_PMODE = "pmode"
LS_HALT  = "halt"

#
# database abstraction
#
class Database:
    def __init__(self,filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)

    def __enter__(self):
        self.crsr = self.conn.cursor()
        return self.crsr

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.crsr = None

    def commit(self):
        self.conn.commit()

    #
    # init
    #
    def setup(self):
        with self as conn:
            #
            # schema 0 (from v1)
            #
            conn.execute("CREATE TABLE IF NOT EXISTS props (id INTEGER PRIMARY KEY ASC,key TEXT UNIQUE,value TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS whitelist (id INTEGER PRIMARY KEY ASC,number TEXT UNIQUE)")
            conn.execute("CREATE INDEX IF NOT EXISTS whitelistNumberIndex ON whitelist (number ASC)")
            conn.execute("CREATE TABLE IF NOT EXISTS blacklist (id INTEGER PRIMARY KEY ASC,number TEXT UNIQUE)")
            conn.execute("CREATE INDEX IF NOT EXISTS blacklistNumberIndex ON blacklist (number ASC)")
            conn.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY ASC,epoch INTEGER,number TEXT,name TEXT)")
            conn.execute("CREATE INDEX IF NOT EXISTS historyEpochIndex ON history (epoch ASC)")

            schema = 0
            for row in conn.execute("SELECT value FROM props WHERE key='schema'"):
                schema = int(row[0])

            #
            # schema 1
            #
            if schema < 1:
                conn.execute("CREATE TABLE log (id INTEGER PRIMARY KEY ASC, time INTEGER, type TEXT, value TEXT)")
                conn.execute("CREATE INDEX IF NOT EXISTS logTimeIndex ON log (time ASC)")
                conn.execute("INSERT INTO props(key, value) VALUES('schema', 1)")
                schema = 1

    #
    # logging
    #
    def _log(self, type, value):
        now = time.time()
        old = 0 # now - 30 * 24 * 60 * 60 # 30 days
        with self as conn:
            conn.execute("INSERT INTO log(time, type, value) VALUES (?, ?, ?)", (time.time(), type, value))
            conn.execute("DELETE FROM log WHERE time < ?", (old, ))
        print("%d: %s %s" % (now, type, value))

    def log(self, text):
        self._log("text", text)

    def log_state(self, state):
        self._log("state", state)
