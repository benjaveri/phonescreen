#!/bin/bash
launchctl load /Library/LaunchDaemons/phonescreen.plist
launchctl start /Library/LaunchDaemons/phonescreen.plist
echo `date` `ps axww | grep usbmodem246802461`
