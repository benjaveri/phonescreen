# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import sys, re
from engine.database import Database

# whitelist.py [del|delete|remove] [number]

def clean(s):
    return re.sub(' +', ' ', s.strip())

try:
    PRIMARY = "whitelist"
    SECONDARY = "blacklist"
    REMOVE = (len(sys.argv) > 2) and sys.argv[1] in ["del","delete","remove"]
    NUMBER = (sys.argv[2] if REMOVE else sys.argv[1]) if len(sys.argv) > 1 else None
except:
    print("Usage: python3 whitelist.py [del|delete|remove <number>]")
    sys.exit(1)

db = Database("numbers.sqlite")

if NUMBER:
    with db as conn:
        conn.execute("DELETE FROM %s WHERE number=?" % SECONDARY,(NUMBER,))
        if REMOVE:
            conn.execute("DELETE FROM %s WHERE number=?" % PRIMARY, (NUMBER,))
        else:
            conn.execute("INSERT OR REPLACE INTO %s(number) VALUES (?)" % PRIMARY,(NUMBER,))

print("%s:" % PRIMARY)
with db as conn:
    numbers = []
    for row in conn.execute("SELECT number FROM %s ORDER BY number" % PRIMARY):
        numbers.append(row[0])
    for number in numbers:
        aliases = set()
        for alias in conn.execute("SELECT DISTINCT name FROM history WHERE number=?", (number,)):
            aliases.add(clean(alias[0]))
        print("%s -> %s" % (number, ", ".join(aliases)))
