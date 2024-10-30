# Chrypnotoad Chat Moderation Bot

A Telegram bot designed to moderate the Chrypnotoad Chat channel. This bot helps prevent spam and manage the channel automatically.

## Features

- Automatic spam detection and removal
- Customizable spam patterns
- Banned word filtering
- User whitelisting
- Admin-only controls
- Action logging

## Setup

1. Create a new bot through @BotFather
2. Add the bot token to config.json
3. Add the bot as an admin to your channel
4. Run the bot using `python3 bot.py`

## Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/addspam <pattern>` - Add a spam pattern
- `/removespam <pattern>` - Remove a spam pattern
- `/listspam` - List all spam patterns
- `/addword <word>` - Add a banned word
- `/removeword <word>` - Remove a banned word
- `/listwords` - List banned words
- `/whitelist <user_id>` - Whitelist a user
- `/unwhitelist <user_id>` - Remove user from whitelist
- `/listwhitelist` - List whitelisted users