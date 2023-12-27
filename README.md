SIMPLE PHONE SCREENER
=====================


This is a simple set of scripts that lets you whitelist and blacklist callers using called-id. It has only been tested
in the US but I think it is trivial to adapt to any other country. All you need is a caller-id & fax capable modem.

There are two versions:
1. v1 is a python 2 based headless monitor. It works on linux and on mac with a little basic tweaking. I
   have used it for many years, non-stop.
1. v2 is a python 3 port of v1 with minor improvements. It includes a live monitor to show stats and actions
   in real time.


python3 -m serial.tools.list_ports
python3 -m serial.tools.miniterm    -- Ctrl+] to exit

