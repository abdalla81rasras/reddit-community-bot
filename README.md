# Reddit Community Bot

A Python Reddit bot designed for a single Reddit community.

## Features

- OAuth authentication
- Monitors new comments
- Replies only when configured trigger phrases are detected
- Optional controlled post creation
- Reply rate limit
- Activity logging
- No voting or karma manipulation
- No private messages
- No cross-subreddit posting
- No mass commenting

## Scope

The application is configured for one subreddit only.

The bot does not attempt to:
- manipulate votes or karma
- bypass moderation
- evade bans
- send unsolicited private messages
- post identical content across multiple communities

## Configuration

Copy `.env.example` to `.env` and fill in the Reddit OAuth credentials.

Do NOT commit `.env` or any client secret/password to GitHub.

## Installation

Install dependencies:

    pip install -r requirements.txt

Run:

    python main.py

## Posting

Automatic posting is disabled by default.

Set `POST_ENABLED = True` only when the intended posting use has been approved and configured for the target community.

## Privacy

The bot does not intentionally collect or sell Reddit user data.

Logs are stored locally and are not intended to be distributed.

## API

This project uses Reddit's Data API through PRAW.
