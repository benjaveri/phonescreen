# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import sys, os
from config import FAX_TIMEOUT, REDIAL_WINDOW
from engine.modem import RealModem
from engine.database import Database
from engine.sm import StateMachine

#
# set up environment
#
path = os.path.join(sys.argv[1], "numbers.sqlite")
port = sys.argv[2]

# database & migrations
db = Database(path)
db.setup()

# we use a fake modem
modem = RealModem(port)

# build state machine
sm = StateMachine(db, modem, FAX_TIMEOUT, REDIAL_WINDOW)

# run until completion
sm.run()
