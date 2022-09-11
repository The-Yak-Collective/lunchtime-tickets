# Lunchtime Tickets

Task management when everyone's out to lunch.

## Setup

1. Fork this repo.

2. Set up the following *repo* secrets in Settings > Security > Secrets > Actions:

	- `ACCESS_TOKEN` - A GitHub access token with the `repo` scope. This is used for those cases where we *want* some action to cause other actions to run (in particular the `issue-to-discord` action), and thus can't use the built-in `GITHUB_TOKEN`.
	- `DISCORD_CHANNEL` - The Discord channel you want ticket notifications to be posted in.
	- `GMAIL_USER` - The Gmail username that should be scanned for incoming tickets (see "Issues from Gmail", below).
	- `GMAIL_PASS` - A [Gmail App Password](https://support.google.com/mail/answer/185833) for the above account.

### Daily Issues to Discord

This action requires `DISCORD_CHANNEL`. It posts a daily summary of all open issues to the specified channel.

### Issue to Discord

This action requires `DISCORD_CHANNEL`. It posts a notification to the specified channel whenever an issue is opened, closed, or re-opened.

### Issues from Gmail

This action requires the `ACCESS_TOKEN`, `GMAIL_USER`, and `GMAIL_PASS` secrets. It scans the specified Gmail inbox looking for new [task-specific emails](https://support.google.com/a/users/answer/9308648) and then converts them into GitHub issues. Processed emails are labeled with `processed-by-lunchtime-tickets` and ignored on subsequent runs. Emails are not otherwise manipulated, so this script is suitable for use with a shared account.

### Recurring Issues

This action requires the `ACCESS_TOKEN` secret. It scans closed issues for issues with a title prefixed by `[RECURRING]` with a body of the following format:

```markdown
frequency: 10
current: 2022-08-28
next: 2022-09-07

This is a body. All GitHub *markdown* is supported.
```

The issue body *must* be structured like this, including the ordering of `frequency`/`current`/`next`.

* `frequency` is how often an issue should be reopened, in days.
* `current` is just a tracking value, and corresponds to the date the issue was last re-opened.
* `next` is the *next* date the issue should be opened.

Whenever this action finds a closed issue whose title is prefixed by `[RECURRING]`, it checks to see if `next` is on or before the current date. If it is, it re-opens the issue, updates `current` to today's date, and updates `next` to the next date that the issue should be opened (`next = current + frequency`).

Once the issue has been handled, it can be closed normally; the action will automatically reopen it when the `next` date rolls around.
