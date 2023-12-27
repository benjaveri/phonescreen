# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
from test.mock_modem import MockModem, CompletedException
from engine.database import Database
from engine.sm import StateMachine

#
# set up test environment
#

# modem program
REDIAL_WINDOW = 1
prog = [
    # blocklist test
    { "at": 1.0, "from":"408--block", "expect":"block" },
    # allowlist test
    { "at": 1.5, "from":"408--allow", "expect":"accept" },
    # immediate redial test 1
    { "at": 2.0, "from":"1234567890", "expect":"pulse" },
    { "at": 2.1, "from":"1234567890", "expect":"accept" },
    # immediate redial test 2
    { "at": 3.0, "from":"0123456780", "expect":"pulse" },
    { "at": 3.1, "from":"0123456781", "expect":"pulse" },
    # non-immediate redial test
    { "at": 4.0, "from":"1234567891", "expect":"pulse" },
    { "at": 6.0, "from":"1234567891", "expect":"pulse" },
    # auto blocklist promotion
    {"at":  7.0, "from": "1234567892", "expect": "pulse"},
    {"at":  8.5, "from": "1234567892", "expect": "pulse"},
    {"at": 10.0, "from": "1234567892", "expect": "pulse"},
    {"at": 11.5, "from": "1234567892", "expect": "pulse"},
    {"at": 13.0, "from": "1234567892", "expect": "block"},
    {"at": 14.5, "from": "1234567892", "expect": "block"},
    # done
    {"at": 15.0, "from": None }
]

# database & migrations
db = Database(":memory:")
db.setup()
with db as conn:
    conn.execute("INSERT INTO allowlist(number) VALUES (?)",("408--allow",))
    conn.execute("INSERT INTO blocklist(number) VALUES (?)",("408--block",))

# we use a fake modem
modem = MockModem(prog)

# build state machine
sm = StateMachine(db, modem, 0, REDIAL_WINDOW)

# wait until completion
try:
    sm.run()
except CompletedException:
    pass
except Exception:
    raise


l = [ "408--allow", "1234567890" ]
c = len(l)
with db as conn:
    for row in conn.execute("SELECT number FROM allowlist"):
        l.remove(row[0])
        c -= 1
assert c == 0
assert len(l) == 0

l = [ "408--block", "1234567892" ]
c = len(l)
with db as conn:
    for row in conn.execute("SELECT number FROM blocklist"):
        l.remove(row[0])
        c -= 1
assert c == 0
assert len(l) == 0
