# Privacy Notes

The bot is intentionally limited.

At runtime it reads new comments from one configured subreddit and the comment author's Reddit username when needed for rate limiting and self-reply prevention.

It does not maintain a persistent database of Reddit users or comments.

Runtime state includes recent comment IDs, reply timestamps, and usernames associated with recent automated replies.

Logs record operational events such as timestamps, action results, Reddit object IDs, and usernames when relevant to an action.

The bot does not implement private messages, voting, multi-subreddit collection, persistent user profiles, or AI training on Reddit data.
