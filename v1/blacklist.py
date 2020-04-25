#!/usr/bin/env python2

# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import sys
from v1.interfaces import *

# blacklist.py [del|delete|remove] [number]

PRIMARY = "blacklist"
SECONDARY = "whitelist"
REMOVE = (len(sys.argv) > 2) and sys.argv[1] in ["del","delete","remove"]
NUMBER = (sys.argv[2] if REMOVE else sys.argv[1]) if len(sys.argv) > 1 else None

db = Database("numbers.sqlite")

if NUMBER:
    with db as conn:
        conn.execute("DELETE FROM %s WHERE number=?" % SECONDARY,(NUMBER,))
        if REMOVE:
            conn.execute("DELETE FROM %s WHERE number=?" % PRIMARY, (NUMBER,))
        else:
            conn.execute("INSERT OR REPLACE INTO %s(number) VALUES (?)" % PRIMARY,(NUMBER,))

print "%s:" % PRIMARY
with db as conn:
    for row in conn.execute("SELECT DISTINCT p.number,h.name FROM %s AS p LEFT JOIN history AS h ON p.number=h.number" % PRIMARY):
        print " %s %s" % (row[0], row[1])