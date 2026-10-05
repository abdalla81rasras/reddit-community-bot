# Reddit Community Bot — V3

A deliberately constrained Reddit community bot for one subreddit.

## Safety defaults
- `DRY_RUN = True`
- `POST_ENABLED = False`
- One configured subreddit only
- Maximum 5 replies/hour
- Maximum 1 automated reply/user/day
- Minimum 60 seconds between replies
- Maximum 20 comments per stream cycle
- No voting, private messages, cross-subreddit automation, or persistent Reddit database

## V3 fix
V2 incorrectly used the size of `recent_comment_ids` as the per-cycle counter.
V3 uses a local `processed` counter, independent of the duplicate-suppression cache.

## Setup
```bash
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env
python main.py
```

The default configuration is dry-run and does not publish or reply.

## Tests
```bash
pytest -q
```

Never commit `.env`, OAuth secrets, tokens, logs, or other credentials.
Do not enable posting/replies until the Reddit application is authorized for the intended use.
