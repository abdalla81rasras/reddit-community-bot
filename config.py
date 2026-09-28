# Reddit community configuration

SUBREDDIT_NAME = "python"

# Comments containing one of these phrases may receive a reply.
TRIGGER_WORDS = [
    "help",
    "question",
    "how do I",
    "error",
]

REPLY_TEXT = """Hi! I'm an automated Reddit bot.

If you're asking a Python question, please include:
- the relevant code
- the error message
- what you expected to happen

This automated account only replies when specific trigger words are detected.
"""

# Disabled by default. Enable only after the intended use has been approved
# and configured for the target community.
POST_ENABLED = False

POST_TITLE = "Weekly Python Community Thread"

POST_BODY = """This is the weekly community thread.

Feel free to share your Python questions and projects.
"""

CHECK_INTERVAL = 60
MAX_COMMENTS_PER_CYCLE = 20
MAX_REPLIES_PER_HOUR = 5
