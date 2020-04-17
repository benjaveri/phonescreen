#!/bin/bash

echo `date` start
echo `date` `ps uxww | grep usbmodem246802461 | grep -v grep`
cd /Users/ben/depot/phonescreen
STR=`ps uxww | grep usbmodem246802461 | grep -v grep`
[ -z "$STR" ] && echo `date` Launching phonescreen
[ -z "$STR" ] && /usr/local/bin/python main.py . /dev/tty.usbmodem246802461 >main.out 2>&1 &
sleep 10
echo `date` `ps uxww | grep usbmodem246802461 | grep -v grep`
echo `date` stop
