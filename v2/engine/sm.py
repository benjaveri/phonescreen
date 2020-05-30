from engine.database import LS_IDLE, LS_BLOCK, LS_PMODE, LS_HALT
import time, sys

class StateMachine:
    def __init__(self, db, modem, fax_timeout, redial_window):
        self.db = db
        self.modem = modem
        self.fax_timeout = fax_timeout
        self.redial_window = redial_window
        self.db.log("SM Started")
        self.db.log_state(LS_IDLE)

    def poll(self):
        try:
            ls = self.modem.poll()
        except Exception as e:
            self.db.log("Exception %s" % e)
            self.db.log_state(LS_HALT)
            sys.exit(1)

        if len(ls) > 0:
            with self.db as conn:
                conn.execute("INSERT INTO history(epoch, number, name) VALUES (?, ?, ?)", (time.time(), ls[1], ls[0]))
        return ls

    def run(self):
        while True:
            # check listener if phone is ringing
            ls = self.poll()
            if len(ls) > 0:
                self.answer(ls[0], ls[1])
            else:
                # idle wait
                time.sleep(.1)

    def answer(self, name, num):
        with self.db as conn:
            # if whitelisted, mark and handle outside of transaction
            allow = False
            for row in conn.execute("SELECT * FROM whitelist WHERE number=?", (num,)):
                allow = True

            # if blacklisted, mark and handle outside of transaction
            block = False
            for row in conn.execute("SELECT * FROM blacklist WHERE number=?", (num,)):
                block = True

        if allow:
            # ring through
            self.db.log("Allowing whitelisted number %s (%s)" % (num, name))
            self.modem.ring_through()
        elif block:
            # answer as fax
            self.db.log("Blocking blacklisted number %s (%s)" % (num, name))
            self.db.log_state(LS_BLOCK)
            self.modem.answer_as_fax(self.fax_timeout)
            self.db.log_state(LS_IDLE)
        else:
            # check this number against history, if we've seen it for a number of times, blacklist it now
            found = False
            with self.db as conn:
                for row in conn.execute("SELECT COUNT(*) FROM history WHERE number=?", (num,)):
                    print(row[0])
                    if int(row[0]) >= 5:
                        found = True
                        break

            if found:
                self.db.log("Blacklisting on fifth call %s (%s)" % (num, name))
                with self.db as conn:
                    conn.execute("INSERT OR REPLACE INTO blacklist(number) VALUES (?)", (num,))
                self.db.log_state(LS_BLOCK)
                self.modem.answer_as_fax(self.fax_timeout)
                self.db.log_state(LS_IDLE)
            else:
                # enter p-mode
                self.pmode(name, num)

    #
    # promiscuous mode (Turing test)
    #
    def pmode(self, name, num):
        # first pulse the phone, to start the Turing test
        self.db. log("Dropping call from new number %s (%s)" % (num, name))
        self.modem.answer_pulse()

        # wait around for a while listening for a redial
        self.db.log("Entering promiscuous mode")
        self.db.log_state(LS_PMODE)
        timeout = time.time() + self.redial_window
        while time.time() < timeout:
            ls = self.poll()
            if len(ls) > 0:
                name2, num2 = ls
                if num == num2:
                    # this is a redial from the same number, whitelist it and ring through
                    self.db.log("Whitelisting and ringing through %s (%s)" % (num, name))
                    with self.db as conn:
                        conn.execute("INSERT INTO whitelist(number) VALUES (?)", (num,))
                    # ring through
                    self.modem.ring_through()
                    # done
                    self.db.log("Leaving promiscuous mode")
                    self.db.log_state(LS_IDLE)
                    return
                else:
                    # someone else called
                    self.db.log("Leaving promiscuous mode")
                    self.db.log_state(LS_IDLE)
                    # handle normally
                    self.answer(name2, num2)
                    return
            else:
                time.sleep(.1)

        # nothing happened, leave pmode
        self.db.log("Leaving promiscuous mode")
        self.db.log_state(LS_IDLE)
