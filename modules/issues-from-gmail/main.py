#!/usr/bin/env python3

# https://docs.python.org/3/library/imaplib.html
# https://developers.google.com/gmail/imap/imap-extensions
# https://support.google.com/mail/answer/7190?hl=en
# https://pygithub.readthedocs.io/en/latest/examples/Issue.html

# Better guides:
# 	https://coderslegacy.com/python/imap-read-emails-with-imaplib/
# 	https://cmsdk.com/python/python-email-quotedprintable-encoding-problem.html

# Import necessary packages
#
import email
import imaplib
import os
import re

from email import policy

# Grab login information from the environment
#
gmail_user = os.environ['GMAIL_USER']
gmail_pass = os.environ['GMAIL_PASS']

# Determine the Gmail user and domain parts
#
gmail_user_part = gmail_user.split("@")[0]
gmail_domain_part = gmail_user.split("@")[1]

# Connect to Gmail
#
server = imaplib.IMAP4_SSL("imap.gmail.com")
server.login(gmail_user, gmail_pass)
server.select('"' + "INBOX" + '"')

# Search for unprocessed messages
#
response, raw_unprocessed_message_set = server.search(None, 'X-GM-RAW "to:(' + gmail_user + ') AND -label:(processed-by-lunchtime-tickets)"')

unprocessed_message_set = ",".join(raw_unprocessed_message_set[0].decode().split())

# Fetch unprocessed message "To" headers
#
response, raw_to_headers = server.fetch(unprocessed_message_set, "(BODY[HEADER.FIELDS (TO)])")

# Loop over raw headers and extract message number and "To" address.
#
# If "To" address contains a "+", then fetch the full ("RFC822")
# message and create a corresponding issue in GitHub.
#
# Regardless of whether the message was turned into an issue, mark it
# as processed so that we don't have to read it again.
#
for raw_to_header in raw_to_headers:
	if isinstance(raw_to_header, tuple):
		message_number = raw_to_header[0].split()[0].decode()
		message_match = re.search(r'[\s,<]' + gmail_user_part + '\+[^@]+\@' + gmail_domain_part + '[>,\s]', raw_to_headers[-2][1].decode())
		if message_match:
			response, raw_message = server.fetch(message_number, "(RFC822)")
			message = email.message_from_string(raw_message[0][1].decode(), policy=policy.default)

			subject = message["Subject"] # subject
			# Extract message content + attachments
			eml = message.as_string() # message as attachment
			# Create ticket (subject, text part, message as attachment, other attachments?)
		server.store(message_number, "+X-GM-LABELS", "(processed-by-lunchtime-tickets)")		

# Walk a message
#
# Probably need to concatenate text/plain and text/html parts? And save off attachments.
#
# for part in message.walk():
# 	print(part.get_content_type())
# 	print(part.get_filename())
# 	print(part.get_content_disposition())
# 	if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
# 		print("")
# 		print(part.get_content())
# 	elif part.get_content_disposition():
# 		print("")
# 		print(part.get_content().decode())
# 	print("")
# 	print("---")
# 	print("")

# Be kind, rewind
#
server.logout()
