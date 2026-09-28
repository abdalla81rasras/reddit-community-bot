import os
import time
import logging
from datetime import datetime, timedelta, timezone

import praw
from dotenv import load_dotenv

from config import (
    SUBREDDIT_NAME,
    TRIGGER_WORDS,
    REPLY_TEXT,
    POST_ENABLED,
    POST_TITLE,
    POST_BODY,
    MAX_COMMENTS_PER_CYCLE,
    MAX_REPLIES_PER_HOUR,
)

load_dotenv()

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/bot.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

processed_comments = set()
reply_times = []


def create_reddit_client():
    values = {
        "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
        "REDDIT_CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET"),
        "REDDIT_USERNAME": os.getenv("REDDIT_USERNAME"),
        "REDDIT_PASSWORD": os.getenv("REDDIT_PASSWORD"),
        "REDDIT_USER_AGENT": os.getenv("REDDIT_USER_AGENT"),
    }

    missing = [key for key, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing environment variables: " + ", ".join(missing)
        )

    return praw.Reddit(
        client_id=values["REDDIT_CLIENT_ID"],
        client_secret=values["REDDIT_CLIENT_SECRET"],
        username=values["REDDIT_USERNAME"],
        password=values["REDDIT_PASSWORD"],
        user_agent=values["REDDIT_USER_AGENT"],
    )


def cleanup_reply_times():
    global reply_times
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    reply_times = [t for t in reply_times if t > cutoff]


def can_reply():
    cleanup_reply_times()
    return len(reply_times) < MAX_REPLIES_PER_HOUR


def contains_trigger(text):
    text = (text or "").lower()
    return any(word.lower() in text for word in TRIGGER_WORDS)


def process_comment(comment):
    if comment.id in processed_comments:
        return

    processed_comments.add(comment.id)

    if not contains_trigger(comment.body):
        return

    if not can_reply():
        logging.warning("Hourly reply limit reached.")
        return

    try:
        comment.reply(REPLY_TEXT)
        reply_times.append(datetime.now(timezone.utc))
        logging.info("Replied to comment %s", comment.id)
        print(f"Replied to comment: {comment.id}")
    except Exception as error:
        logging.error("Failed to reply to %s: %s", comment.id, error)


def create_post(reddit):
    if not POST_ENABLED:
        logging.info("Automatic posting is disabled.")
        return

    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    try:
        submission = subreddit.submit(
            title=POST_TITLE,
            selftext=POST_BODY,
        )
        logging.info("Created post: %s", submission.id)
        print(f"Created post: {submission.id}")
    except Exception as error:
        logging.error("Failed to create post: %s", error)


def monitor_comments(reddit):
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    logging.info("Monitoring r/%s", SUBREDDIT_NAME)
    print(f"Monitoring r/{SUBREDDIT_NAME}...")

    while True:
        try:
            comments = subreddit.stream.comments(skip_existing=True)

            for index, comment in enumerate(comments):
                if index >= MAX_COMMENTS_PER_CYCLE:
                    break
                process_comment(comment)

        except Exception as error:
            logging.error("Comment stream error: %s", error)
            time.sleep(30)


def main():
    logging.info("Starting Reddit Community Bot")

    reddit = create_reddit_client()

    try:
        me = reddit.user.me()
        print(f"Logged in as: u/{me.name}")
        logging.info("Logged in as u/%s", me.name)
    except Exception as error:
        logging.exception("Authentication verification failed")
        raise error

    create_post(reddit)
    monitor_comments(reddit)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        logging.info("Bot stopped by user.")
    except Exception as error:
        print(f"Fatal error: {error}")
        logging.exception("Fatal error")
