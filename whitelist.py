#!/usr/bin/env python

# BSD 3-Clause License
#
# Copyright (c) 2017 by Ben de Waal, All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import sys
from interfaces import *

# whitelist.py [del|delete|remove] [number]

PRIMARY = "whitelist"
SECONDARY = "blacklist"
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
    for row in conn.execute("SELECT number FROM %s" % PRIMARY):
        print " %s" % row[0]
