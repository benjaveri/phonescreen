# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import sys, re
from engine.database import Database

db = Database("numbers.sqlite")
with db as conn:
    for row in conn.execute("SELECT * from log ORDER BY time"):
        print(row)
