#!/bin/bash
echo `date` `ps axww | grep usbmodem246802461`
launchctl stop /Library/LaunchDaemons/phonescreen.plist
launchctl unload /Library/LaunchDaemons/phonescreen.plist
