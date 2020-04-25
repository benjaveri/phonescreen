#!/usr/bin/env python2

# BSD 3-Clause License -> see /LICENSE
# Copyright (c) 2017-2020 by Ben de Waal, All rights reserved.
#
import datetime
from v1.interfaces import *

db = Database("numbers.sqlite")
with db as conn:
    print "HISTOGRAM"
    for row in conn.execute("SELECT number,name,COUNT(number) FROM history GROUP BY number ORDER BY COUNT(number)"):
        print "%s %s %s" % (row[0],row[1],row[2])
    print

    print "HISTORY"
    for row in conn.execute("SELECT epoch,number,name FROM history"):
        print "%s %s %s" % (datetime.datetime.fromtimestamp(int(row[0])).strftime('%Y-%m-%d %H:%M:%S'),row[1],row[2])
        
