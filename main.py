import logging
import os
import re
import time
from collections import deque
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from config import (
    CHECK_INTERVAL, MAX_COMMENTS_PER_CYCLE, MAX_REPLIES_PER_HOUR,
    MAX_REPLIES_PER_USER_PER_DAY, MIN_REPLY_INTERVAL_SECONDS,
    POST_BODY, POST_ENABLED, POST_INTERVAL_HOURS, POST_TITLE,
    SUBREDDIT_NAME, TRIGGER_PHRASES, DRY_RUN,
)

load_dotenv()
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "bot.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("reddit-community-bot")

USER_AGENT = os.getenv("REDDIT_USER_AGENT", "python:reddit-community-bot:3.0 (by /u/unknown)")
subreddit = None

def initialize_reddit():
    """Create the Reddit client only when the bot is actually started."""
    import praw

    global subreddit
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=USER_AGENT,
    )
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

# Runtime-only state; no Reddit data is persisted.
recent_comment_ids = deque(maxlen=500)
reply_timestamps = deque()
user_reply_timestamps = {}
last_post_at = None
last_reply_at = None


def validate_environment():
    required = [
        "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET",
        "REDDIT_USERNAME", "REDDIT_PASSWORD", "REDDIT_USER_AGENT",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))
    if "reddit-community-bot" not in USER_AGENT.lower():
        logger.warning("USER_AGENT should identify this application clearly.")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains_trigger(text: str) -> bool:
    normalized = normalize(text)
    return any(phrase.lower() in normalized for phrase in TRIGGER_PHRASES)


def prune_reply_limits(now: datetime):
    hour_ago = now - timedelta(hours=1)
    while reply_timestamps and reply_timestamps[0] < hour_ago:
        reply_timestamps.popleft()

    day_ago = now - timedelta(days=1)
    for username, timestamps in list(user_reply_timestamps.items()):
        while timestamps and timestamps[0] < day_ago:
            timestamps.popleft()
        if not timestamps:
            del user_reply_timestamps[username]


def can_reply(username: str, now: datetime) -> tuple[bool, str]:
    prune_reply_limits(now)
    if len(reply_timestamps) >= MAX_REPLIES_PER_HOUR:
        return False, "hourly global limit reached"
    user_timestamps = user_reply_timestamps.get(username, deque())
    if len(user_timestamps) >= MAX_REPLIES_PER_USER_PER_DAY:
        return False, "daily per-user limit reached"
    if last_reply_at is not None:
        if (now - last_reply_at).total_seconds() < MIN_REPLY_INTERVAL_SECONDS:
            return False, "minimum reply interval not reached"
    return True, "ok"


def record_reply(username: str, now: datetime):
    global last_reply_at
    reply_timestamps.append(now)
    user_reply_timestamps.setdefault(username, deque()).append(now)
    last_reply_at = now


def should_post(now: datetime) -> bool:
    if not POST_ENABLED:
        return False
    if last_post_at is None:
        return True
    return (now - last_post_at) >= timedelta(hours=POST_INTERVAL_HOURS)


def publish_community_post(now: datetime):
    global last_post_at
    if DRY_RUN:
        logger.info("DRY_RUN: would create community post: %s", POST_TITLE)
        last_post_at = now
        return
    submission = subreddit.submit(title=POST_TITLE, selftext=POST_BODY)
    logger.info("Created submission id=%s", submission.id)
    last_post_at = now


def handle_comment(comment):
    author = comment.author
    if author is None:
        logger.info("Skipping deleted/unknown author comment id=%s", comment.id)
        return

    username = author.name.lower()
    bot_username = os.getenv("REDDIT_USERNAME", "").lower()
    if username == bot_username:
        return

    if comment.id in recent_comment_ids:
        return
    recent_comment_ids.append(comment.id)

    if not contains_trigger(comment.body or ""):
        return

    now = datetime.now(timezone.utc)
    allowed, reason = can_reply(username, now)
    if not allowed:
        logger.info("Skipping comment id=%s author=%s reason=%s", comment.id, username, reason)
        return

    if DRY_RUN:
        logger.info("DRY_RUN: would reply to comment id=%s author=%s", comment.id, username)
        record_reply(username, now)
        return

    try:
        comment.reply(REPLY_TEXT)
        record_reply(username, now)
        logger.info("Replied to comment id=%s author=%s", comment.id, username)
    except Exception:
        logger.exception("Failed to reply to comment id=%s", comment.id)


def process_comment_cycle(comments):
    """Process at most MAX_COMMENTS_PER_CYCLE items in this cycle."""
    processed = 0
    for comment in comments:
        if comment is None:
            break
        handle_comment(comment)
        processed += 1
        if processed >= MAX_COMMENTS_PER_CYCLE:
            break
    return processed


def run():
    validate_environment()
    initialize_reddit()
    logger.info(
        "Starting bot | subreddit=%s | dry_run=%s | post_enabled=%s",
        SUBREDDIT_NAME, DRY_RUN, POST_ENABLED,
    )

    now = datetime.now(timezone.utc)
    if should_post(now):
        try:
            publish_community_post(now)
        except Exception:
            logger.exception("Failed to create scheduled community post")

    while True:
        try:
            process_comment_cycle(
                subreddit.stream.comments(skip_existing=True, pause_after=-1)
            )
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
            break
        except Exception:
            logger.exception("Main loop error; sleeping before retry.")
            time.sleep(max(CHECK_INTERVAL, 30))


if __name__ == "__main__":
    run()
