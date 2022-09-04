# We may want issues-from-gmail to ALWAYS process some emails. For
# example, Google account notification (which we can't send to a
# +address):
#
# noreply@google.com
# no-reply@accounts.google.com
# etc.
#
# For consistency, we want to store the list of emails we always process
# in a GitHub repository secret. But we can't view this secret, so how
# do we update it?
#
# Instead, let us have THREE secrets:
#
# GMAIL_ALWAYS_PROCESS
# GMAIL_ALWAYS_PROCESS_ADD
# GMAIL_ALWAYS_PROCESS_REMOVE
#
# This script dows the following:
#
# 1. Add emails (space, comma, tab, or pipe separated) from
#    GMAIL_ALWAYS_PROCESS_ADD to GMAIL_ALWAYS_PROCESS.
# 2. Remove emails (space, comma, tab, or pipe separated) from
#    GMAIL_ALWAY_PROCESS_REMOVE from GMAIL_ALWAYS_PROCESS.
# 3. Deduplicate GMAIL_ALWAYS_PROCESS.
# 4. Update the stored GMAIL_ALWAYS_PROCESS secret with the new version
#    derived in steps 1 - 3.
# 5. Update GMAIL_ALWAYS_PROCESS_ADD and GMAIL_ALWAYS_PROCESS_REMOVE to
#    the empty string.
#
# We then have issues-from-gmail pull in GMAIL_ALWAYS_PROCESS.
