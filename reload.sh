#!/bin/bash
echo `date` `ps axww | grep usbmodem246802461`
launchctl stop /Library/LaunchDaemons/phonescreen.plist
launchctl unload /Library/LaunchDaemons/phonescreen.plist
rm phonescreen.err
rm phonescreen.out
cp phonescreen.plist /Library/LaunchDaemons/phonescreen.plist
launchctl load /Library/LaunchDaemons/phonescreen.plist
launchctl start /Library/LaunchDaemons/phonescreen.plist
echo `date` `ps axww | grep usbmodem246802461`
