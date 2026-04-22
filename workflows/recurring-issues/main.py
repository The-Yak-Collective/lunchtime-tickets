#!/usr/bin/env python3

# Import necessary packages
#
import os

from datetime import datetime, timedelta
from github import Github

# Grab login information from the environment
#
github_token = os.environ["ACCESS_TOKEN"]
github_repo = os.environ["GITHUB_REPOSITORY"]

# Connect to GitHub
#
gh = Github(github_token)
lunchtime_tickets = gh.get_repo(github_repo)

# Pull all of our closed issues
#
closed_issues = lunchtime_tickets.get_issues(state='closed')

# Loop over closed issues looking for recurring issues
#
for issue in closed_issues:
	if issue.title.lower().startswith("[recurring]"):
		try:
			# Extract frequency/current/next
			#
			# FIXME: we need to add code to detect whether
			# UNIX (\n) or Windows (\r\n) line endings are
			# being used, and then adapt the split() here
			# and the if-block that follows accordingly, as
			# I'm not 100% sure that the \r\n -> \n
			# transition isn't an artifact of different
			# clients being used.
			#
			body_array = issue.body.split("\n",3)
			frequency = int(body_array[0].split(": ")[1])
			current = datetime.strptime(body_array[1].split(": ")[1], "%Y-%m-%d")
			next = datetime.strptime(body_array[2].split(": ")[1], "%Y-%m-%d")

			# Only continue processing if `next` <= today
			#
			if next <= datetime.today():
				current = datetime.today()
				next = datetime.today() + timedelta(days = frequency)

				issue_body = "frequency: " + str(frequency) + "\n"
				issue_body += "current: " + current.strftime("%Y-%m-%d") + "\n"
				issue_body += "next: " + next.strftime("%Y-%m-%d") + "\n" 
				issue_body += body_array[3]

				issue.edit(body = issue_body, state = "open")

		except:
			lunchtime_tickets.create_issue(title = "Failed to process recurring issue #" + str(issue.number), body = "[" + issue.title + "](" +  issue.url + ")")
