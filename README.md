SIMPLE PHONE SCREENER
=====================

This is a simple set of scripts that lets you whitelist and blacklist callers using called-id. It has only been tested
in the US but I think it is trivial to adapt to any other country. All you need is a caller-id & fax capable modem.

This works for land lines. Not going to work for your cell phone. Sorry.

I am using a Zoom 3095 mini USB modem. https://smile.amazon.com/gp/product/B001FCIOSW

Mine is connected to a linux box in the basement. The phone line is run in parallel with the rest of the phones in my
home.

You can see some pictures of my setup here: https://imgur.com/a/OFWS9

I am open to pull requests to make the system better. It would be really fun to connect to the government's do-not-call
complaint department, and also to help "spamhaus"-like services with white- and black-list information. Also cool is to 
retrieve assistance evaluating the likelihood of spam calls and acting on it.



ALGORITHM
---------


When an incoming call is detected, the code identifies the caller by their number according to the caller ID information
that is sent after the first ring.

If the number is whitelisted, it will ring though. This will also allow you to pick up, or your answering machine to 
take a message.

If the number is blacklisted, the modem will answer as a fax machine, discouraging future calls. Many robo-diallers will
remove your number from their records if they determine it is attended by their robot kin. They dont have much to say to
each other.

If the number isn't on any of the above lists, it will do the following:
  1. If it has never been seen before, or it has been more than one minute since they called since, the modem
     will pick up and hang up immediately. To humans this would seem like an oddity and they will likely dial again.
     The robo-dialling overlords however will usually move on. Not a very social kind are they?
  2. If the person called within the last minute, it will
            a) let the call ring through,
            b) whitelist their number,
            c) and thus subsequent calls will just ring through as well.

I have provided two scripts that helps you manage the white and black lists. You have to run them as root, but only
because systemd runs as root and elevates permissions of the number.sqlite database file.

Show history of calls: <br/>
`$ ./history.py`

White list a number (also removes it from blacklist if it was there) <br/>
`$ ./whitelist.py 9995551212`

Black list a number (also removes it from whitelist if it was there) <br/>
`$ ./blacklist.py 9995551212`

List all numbers on white list <br/>
`$ ./whitelist.py`

List all numbers on black list <br/>
`$ ./blacklist.py`

Removes a number from both lists <br/>
`$ ./whitelist.py remove 6505551212` <br/>
 or <br/>
`$ ./blacklist.py remove 6505551212`



TESTING AND INSTALLATION
------------------------

To start out with, make sure you know which serial port your modem is connected to. I just did "ls /dev/tty*" before
and after pluggin it in to see what changed. You can use "screen </dev/whatever>" to connect manually and try some
AT commands (like ATE1, then ATZ0, which will show OK returns). Ctrl+A followed by '/' will exit.

Once you know this, you can test from the command line by issuing:
$ python main.py . </dev/your-serial-port>

When it's running, use your cell phone or a friend to call you. You should be able to reproduce the behavior listed
above.

Once you're happy, you can change the phonescreen.service file to reflect your installation directories and your modem's
serial port, and make it run automagically using systemd. See the .service file for installation details.



Have fun!
