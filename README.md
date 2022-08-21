# Lunchtime Tickets

Task management when everyone's out to lunch.

## Setup

1. Fork this repo.

2. Set up the follwing *repo* secrets in Settings > Security > Secrets > Actions:

	- `ACCESS_TOKEN` - A GitHub access token with the `repo` scope. (Yes, this is much broader than we need. Unfortunately GitHub doesn't offer a scope that's restricted only to issues. We can't use the automatically generated `GITHUB_TOKEN` here, as we *want* some flows to cause others - in particular the `issue-to-discord` action - to be run.)
	- `DISCORD_CHANNEL` - The Discord channel you want ticket notifications to be posted in.
	- `GMAIL_USER` - The Gmail username that should be scanned for incoming tickets (see "Issues from Gmail", below).
	- `GMAIL_PASS` - A [Gmail App Password](https://support.google.com/mail/answer/185833) for the above account.
	- `REPO_NAME` - The (forked) repo name, including the user/org part. For example, `The-Yak-Collective/lunchtime-tickets`.

### Daily Issues to Discord

This action requires `DISCORD_CHANNEL` and `REPO_NAME`. It posts a daily summary of all open issues to the specified channel.

### Issue to Discord

This action requires `DISCORD_CHANNEL`. It posts a notification to the specified channel whenever an issue is opened, closed, or re-opened.

### Issues from Gmail

This action requires the `ACCESS_TOKEN`, `GMAIL_USER`, `GMAIL_PASS`, and `REPO_NAME` secrets. It scans the specified Gmail inbox looking for new [task-specific emails](https://support.google.com/a/users/answer/9308648) and then converts them into GitHub issues. Processed emails are labeled with `processed-by-lunchtime-tickets` and ignored on subsequent runs. Emails are not otherwised manipulated, so this script is suitable for use with a shared account.

## Initial Meeting Notes

Maier wants the main interface to be Discord.

Getting information *into* Discord is straight-forward.

Flow:

* Event comes in from some source (Gmail, GitHub issue, etc.).
	* Triggers in GitHub: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows
* Push that event as a “task” to a channel in Discord.
* If a task is a bigger thing, then someone may take “ownership” first.
* There may be a place where someone goes to get more details about the task.
	* Details might be documentation in Roam, or they might be more information from the body of an incoming email. Might even be something else.
* Time passes (maybe), and someone indicates that they’ve done the task.
* Someone (else) confirms that the task was done.
* Profit!
	* People who need to get something out of this: The person doing the task *and* the person confirming.

Rough architecture:

* Event engine(s)
	* Ingest incoming tasks
	* Potentially write some information into the system that holds supplemental task data
* Some system(s) that hold supplemental task data
* Discord interaction bot
* Some system(s) that hold task state information
	* This could very well be the same system that hold supplemental task data
* Bridge between the task state and some kind of reward system

Options for state + supplemental data:

* Roam
	* Can hold documentation
	* Could hold supplemental task information, but it’s kinda unorganized
* GitHub Issues
	* Hold supplemental task information
	* Have a sense of ownership
	* Have a sense of state

Bot/Engine options:

* GitHub Actions
	* Could be used to ingest incoming data
	* Could be used to periodically sync task state info to reward system
	* *Not* suitable for on-demand interaction
* Vultr
	* Could do all of the botty-things
	* We need to actively manage system state if we’re here

Some bots are actually storing state in Vultr.

Two types of users:

* The person who defines the task
	* Probably easier to do in GitHub
* The person who *does* the task

Webhooks:

* GitHub can hit a webhook when an event occurs
* GitHub Actions can receive a webhook
	* https://mainawycliffe.dev/blog/github-actions-trigger-via-webhooks/
	* https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event
* Discord can receive webhooks per-channel
* Discord *does not* have outgoing webhooks without bots

Simplest case: Just push tasks from GitHub Issues into a Discord channel.

Maybe we track state with a label? Can we stop people from closing issues themselves?

GitHub Actions needs to make sure that issues get re-opened if they’ve been improperly closed.
