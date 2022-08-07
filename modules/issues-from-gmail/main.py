#!/usr/bin/env python3

# https://docs.python.org/3/library/imaplib.html
# https://developers.google.com/gmail/imap/imap-extensions
# https://support.google.com/mail/answer/7190?hl=en
# https://pygithub.readthedocs.io/en/latest/examples/Issue.html
# https://github.com/sibson/ghinbox

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

# Unfortunately, raw_unprocessed_message_set is a single element list
# containing a byte string of message IDs, and we need a (regular)
# comma-separated string of message IDs for future commands. So we
# convert it here.
#
unprocessed_message_set_string = ",".join(raw_unprocessed_message_set[0].decode().split())

# Fetch unprocessed message "To" headers
#
response, raw_ToField_headers = server.fetch(unprocessed_message_set_string, "(BODY[HEADER.FIELDS (TO)])")

# Loop over raw headers and extract message number and "To" address.
#
# If "To" address contains a "+", then fetch the full ("RFC822")
# message and create a corresponding issue in GitHub.
#
# Regardless of whether the message was turned into an issue, mark it
# as processed so that we don't have to read it again.
#
for raw_ToField_header in raw_ToField_headers:
	if isinstance(raw_ToField_header, tuple):
		message_number = raw_ToField_header[0].decode().split()[0]

		# TODO - This will still match to strings like
		# "yakcollective.org+foo@gmail.com <evil.email@example.com>".
		# If we wanted to do this right, we'd create a list of all
		# "To" emails, parse out the *actual* email address (ignoring
		# the "friendly name"), and *then* match.
		#
		message_match = re.search(r'[\s,<]' + gmail_user_part + '\+[^@]+\@' + gmail_domain_part + '[>,\s]', raw_ToField_header[1].decode())

		if message_match:
			response, raw_message = server.fetch(message_number, "(RFC822)")
			message = email.message_from_string(raw_message[0][1].decode(), policy=policy.default)

			subject = message["Subject"] # Subject
			eml = message.as_string() # Message as attachment

			# Walk through message parts and extract MIME parts.
			# 
			# Parts that are text/plain or text/html without a content
			# disposition are treated as the message body; if multiple
			# such parts of the same type are found, we concatenate
			# them. Parts without a content disposition that are *not*
			# of type text/plain or text/html are ignored.
			#
			# Parts that *have* a content disposition and a file name
			# are treated as attachments. Parts with a content
			# disposition and no file name are ignored.
			#
			# TODO - Ideally, we should separately track content that
			# has a content disposition of "inline" and then try to
			# re-embed it when creating the issue in GitHub.
			#
			message_body = {
				"text": "",
				"html": ""
			}
			message_attachments = []

			for message_part in message.walk():
				if not message_part.get_content_type().startswith("multipart/"):
					if not message_part.get_content_disposition() and (message_part.get_content_type() == "text/plain" or message_part.get_content_type() == "text/html"):
						if message_part.get_content_type() == "text/plain":
							message_body["text"] = (message_body["text"] + "\n\n" + message_part.get_content()).strip()
						elif message_part.get_content_type() == "text/html":
							message_body["html"] = (message_body["html"] + message_part.get_content()).strip()
					elif message_part.get_content_disposition():
						attachment_data = {
							"type": message_part.get_content_type(),
							"name": message_part.get_filename(),
							"data": message_part.get_content()
						}
						message_attachments.append(attachment_data)

			# TODO - Create ticket (subject, text part, message as attachment, other attachments?)

		server.store(message_number, "+X-GM-LABELS", "(processed-by-lunchtime-tickets)")		

# Be kind, rewind
#
server.logout()
