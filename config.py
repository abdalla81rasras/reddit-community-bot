SUBREDDIT_NAME = "python"
TRIGGER_PHRASES = ["how do i", "how can i", "python error", "python question"]

REPLY_TEXT = """Hi! I'm an automated community bot.

If you're asking a Python question, please include:
- the relevant code
- the exact error message
- what you expected to happen

If this automated reply is not relevant, please ignore it.
"""

DRY_RUN = True
POST_ENABLED = False
POST_TITLE = "Weekly Python Community Thread"
POST_BODY = "This is the weekly community thread.\n\nFeel free to share Python questions and projects."
POST_INTERVAL_HOURS = 168

MAX_REPLIES_PER_HOUR = 5
MAX_REPLIES_PER_USER_PER_DAY = 1
MIN_REPLY_INTERVAL_SECONDS = 60

CHECK_INTERVAL = 60
MAX_COMMENTS_PER_CYCLE = 20
