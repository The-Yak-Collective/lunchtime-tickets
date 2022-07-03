#!/usr/bin/env python3

# https://docs.python.org/3/library/imaplib.html
# https://developers.google.com/gmail/imap/imap-extensions
# https://support.google.com/mail/answer/7190?hl=en

# Import necessary packages
#
import imaplib
import os

# Grab login information from the environment
#
gmail_user = os.environ['GMAIL_USER']
gmail_pass = os.environ['GMAIL_PASS']

# Connect to Gmail
#
server = imaplib.IMAP4_SSL("imap.gmail.com")
server.login(gmail_user, gmail_pass)
server.select('"' + "INBOX" + '"')
# server.search(None, 'X-GM-RAW "to:(yakcollective.org+atest@gmail.com) -label:(lunchtime-tickets)"')
# server.store("2071", "+X-GM-LABELS", "(lunchtime-tickets)")
server.logout()
