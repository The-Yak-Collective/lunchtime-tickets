#!/usr/bin/env python3

# https://docs.python.org/3/library/imaplib.html
# https://developers.google.com/gmail/imap/imap-extensions
# https://support.google.com/mail/answer/7190?hl=en
# https://pygithub.readthedocs.io/en/latest/examples/Issue.html

# This one:
# 	https://coderslegacy.com/python/imap-read-emails-with-imaplib/

# Import necessary packages
#
import email
import imaplib
import os
import re

# Grab login information from the environment
#
gmail_user = os.environ['GMAIL_USER']
gmail_pass = os.environ['GMAIL_PASS']

# Connect to Gmail
#
server = imaplib.IMAP4_SSL("imap.gmail.com")
server.login(gmail_user, gmail_pass)
server.select('"' + "INBOX" + '"')

# Search for unprocessed messages
#
response, raw_unprocessed_message_set = server.search(None, 'X-GM-RAW "to:(yakcollective.org@gmail.com) AND -label:(processed-by-lunchtime-tickets)"')

unprocessed_message_set = ",".join(message_set[0]decode().split()) 

# Fetch unprocessed message "To" headers
#
response, raw_to_headers = server.fetch(unprocessed_message_set, "(BODY[HEADER.FIELDS (TO)])")

unprocessed_messages = []

for raw_to_header in raw_to_headers:
	if isinstance(raw_to_header, tuple):
		message_number = raw_to_header[0].split()[0].decode()
		message_to = re.sub(r'[<>]', '', raw_to_header[1].decode().split()[-1])
		unprocessed_messages.append((message_number, message_to))

# Loop over array A
#     If plus
#         Add to array B
# Fetch message RFC822 from array B
#     Create tickets from array B (subject, text part, message as attachment, other attachments?)
# Tag all array A as processed

# server.store("2071", "+X-GM-LABELS", "(processed-by-lunchtime-tickets)")
server.logout()
