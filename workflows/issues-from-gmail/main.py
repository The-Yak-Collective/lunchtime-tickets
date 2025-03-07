#!/usr/bin/env python3

# Import necessary packages
#
import email
import imaplib
import os
import re

from email import policy
from github import Github
from markdownify import markdownify as md
from secrets_manager import secrets_manager

# Grab login information from the environment
#
github_token = os.environ["ACCESS_TOKEN"]
github_repo = os.environ["GITHUB_REPOSITORY"]
gmail_user = os.environ["GMAIL_USER"]
gmail_pass = os.environ["GMAIL_PASS"]

# Determine the Gmail user and domain parts
#
gmail_user_part = gmail_user.split("@")[0]
gmail_domain_part = gmail_user.split("@")[1]

# Connect to GitHub
#
gh = Github(github_token)
lunchtime_tickets = gh.get_repo(github_repo)

# Pull list of sender emails to always process. We need to include
# repo_handle here so that the secret containing the sender emails
# can be updated.
#
sender_always_process_list = secrets_manager.update(repo_handle = lunchtime_tickets, var_name = "GMAIL_ALWAYS_PROCESS", base = "", add = "ADD", remove = "REMOVE", separator = "_")

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

# If len(unprocessed_message_set_string) == 0, then there are no new
# messages and we can just bail.
#
if len(unprocessed_message_set_string) != 0:

	# Fetch unprocessed message "To" and "From" headers
	#
	response, raw_ToField_headers = server.fetch(unprocessed_message_set_string, "(BODY[HEADER.FIELDS (TO)])")
	response, raw_FromField_headers = server.fetch(unprocessed_message_set_string, "(BODY[HEADER.FIELDS (FROM)])")

	# Set of messages to process (later)
	#
	messages_to_process = set()
	all_messages = set()

	# Loop over raw headers and extract message number and "To"
	# address.
	#
	# If a "To" address contains a "+" then add it to
	# messages_to_process.
	#
	for raw_ToField_header in raw_ToField_headers:
		if isinstance(raw_ToField_header, tuple):
			message_number = raw_ToField_header[0].decode().split()[0]

			# FIXME - This will still match to strings like
			# "yakcollective.org+foo@gmail.com <evil.email@example.com>".
			# If we wanted to do this right, we'd create a list of all
			# "To" emails, parse out the *actual* email address
			# (ignoring the "friendly name"), and *then* match.
			#
			message_match = re.search(r'[\s,<]' + gmail_user_part + r'\+[^@]+\@' + gmail_domain_part + r'[>,\s]', raw_ToField_header[1].decode())

			# Add matched messages to messages_to_process
			#
			if message_match:
				messages_to_process.add(message_number)
			
			# Regardless of whether we had a match or not, add the
			# message to all_messages.
			# 
			all_messages.add(message_number)

	# Loop over raw headers and extract message number and "From"
	# address.
	#
	# If a "from" address is in sender_always_process_list then add it
	# to messages_to_process.
	#
	for raw_FromField_header in raw_FromField_headers:
		if isinstance(raw_FromField_header, tuple):
			message_number = raw_FromField_header[0].decode().split()[0]

			# Extract "From" address
			#
			from_email = re.sub(r'>$', '', re.sub(r'^.*<', '', re.sub(r'^From: ', '', raw_FromField_header[1].decode().strip())))

			# If from_email is in sender_always_process_list, then we
			# consider the message as matching.
			#
			if from_email in sender_always_process_list:
				messages_to_process.add(message_number)
			
			# Regardless of whether we had a match or not, add the
			# message to all_messages.
			# 
			all_messages.add(message_number)

	# Create GitHub tickets for all messages in messages_to_process
	#
	for message_number in messages_to_process:
		response, raw_message = server.fetch(message_number, "(RFC822)")
		message = email.message_from_string(raw_message[0][1].decode(), policy=policy.default)

		# Walk through message parts and extract the message contents.
		# 
		# Parts that are text/plain or text/html without a content
		# disposition are treated as the message body; if multiple such
		# parts of the same type are found, we concatenate them. Parts
		# without a content disposition that are *not* of type
		# text/plain or text/html are ignored.
		#
		# Parts that *have* a content disposition and a file name are
		# (normally) attachments. We don't deal with these here, as the
		# GitHub API doesn't allow us to add attachments to issues right
		# now.
		#
		message_body = {
			"text": "",
			"html": ""
		}

		for message_part in message.walk():
			if not message_part.get_content_type().startswith("multipart/"):
				if not message_part.get_content_disposition() and (message_part.get_content_type() == "text/plain" or message_part.get_content_type() == "text/html"):
					if message_part.get_content_type() == "text/plain":
						message_body["text"] = (message_body["text"] + "\n\n" + message_part.get_content().strip()).strip()
					elif message_part.get_content_type() == "text/html":
						message_body["html"] = (message_body["html"] + message_part.get_content().strip()).strip()

		# It's very rare these days that much care is taken with the
		# plain text part of messages. If an HTML part exists, we will
		# almost always get a nicer issue by converting this into
		# Markdown than by preferring the plain text part.
		#
		# We do a quick-and-dirty replacement to turn <div> and </div>
		# tags into <p> and </p> tags, as a lot of email clients like to
		# wrap things in <div> tags these days, rather than using <p>
		# tags.
		#
		# We also need to deal with the <div>-<br>-<div> sequence
		# without busting the ability to use <br> tags in general. Hence
		# the wacky replacement *after* conversion.
		#
		if message_body["html"] != "":
			message_body["text"] = md(message_body["html"].replace("<div ", "<p ").replace("<div>", "<p>").replace("</div>", "</p>"), heading_style = "ATX").replace("\n\n  \n\n\n", "\n\n").strip()

		# Create ticket
		#
		lunchtime_tickets.create_issue(title = message["Subject"], body = message_body["text"])

	# Label every message in all_messages
	#
	server.store(",".join(list(all_messages)), "+X-GM-LABELS", "(processed-by-lunchtime-tickets)")

# Be kind, rewind
#
server.logout()
