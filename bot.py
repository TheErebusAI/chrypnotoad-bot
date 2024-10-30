#!/usr/bin/env python3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import re
import json
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
CONFIG_FILE = 'config.json'
config = {
    'token': None,
    'channel_id': None,
    'owner_id': None,
    'spam_patterns': [
        r'(?i)t\.me/\+',  # Telegram invite links
        r'(?i)https?://(?!t\.me)',  # Non-Telegram links
        r'(?i)buy|sell|crypto|bitcoin|eth|bnb|pump',  # Crypto spam
        r'(?i)admin.*(?:needed|required|wanted)',  # Admin requests
        r'(?i)earn.*money|make.*money',  # Money schemes
    ],
    'banned_words': [],
    'whitelisted_users': []
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            loaded_config = json.load(f)
            config.update(loaded_config)

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    if update.effective_user.id != config['owner_id']:
        return
    await update.message.reply_text('Bot is running! I will help manage your channel.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    if update.effective_user.id != config['owner_id']:
        return
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/addspam <pattern> - Add a spam pattern
/removespam <pattern> - Remove a spam pattern
/listspam - List all spam patterns
/addword <word> - Add a banned word
/removeword <word> - Remove a banned word
/listwords - List banned words
/whitelist <user_id> - Whitelist a user
/unwhitelist <user_id> - Remove user from whitelist
/listwhitelist - List whitelisted users
"""
    await update.message.reply_text(help_text)

async def is_spam(message: str) -> bool:
    """Check if a message matches any spam patterns."""
    for pattern in config['spam_patterns']:
        if re.search(pattern, message):
            return True
    for word in config['banned_words']:
        if word.lower() in message.lower():
            return True
    return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    message = update.channel_post or update.message
    
    if not message:
        return

    # Skip messages from whitelisted users
    if message.from_user and message.from_user.id in config['whitelisted_users']:
        return

    # Check for spam
    if await is_spam(message.text):
        try:
            await message.delete()
            logging.info(f"Deleted spam message: {message.text[:100]}...")
        except Exception as e:
            logging.error(f"Error deleting message: {e}")

async def add_spam_pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new spam pattern."""
    if update.effective_user.id != config['owner_id']:
        return
    if not context.args:
        await update.message.reply_text("Please provide a pattern to add.")
        return
    pattern = ' '.join(context.args)
    if pattern not in config['spam_patterns']:
        config['spam_patterns'].append(pattern)
        save_config()
        await update.message.reply_text(f"Added spam pattern: {pattern}")
    else:
        await update.message.reply_text("This pattern already exists.")

async def remove_spam_pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a spam pattern."""
    if update.effective_user.id != config['owner_id']:
        return
    if not context.args:
        await update.message.reply_text("Please provide a pattern to remove.")
        return
    pattern = ' '.join(context.args)
    if pattern in config['spam_patterns']:
        config['spam_patterns'].remove(pattern)
        save_config()
        await update.message.reply_text(f"Removed spam pattern: {pattern}")
    else:
        await update.message.reply_text("Pattern not found.")

async def list_spam_patterns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all spam patterns."""
    if update.effective_user.id != config['owner_id']:
        return
    patterns = '\n'.join(config['spam_patterns'])
    await update.message.reply_text(f"Spam patterns:\n{patterns}")

async def add_banned_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a banned word."""
    if update.effective_user.id != config['owner_id']:
        return
    if not context.args:
        await update.message.reply_text("Please provide a word to ban.")
        return
    word = ' '.join(context.args)
    if word not in config['banned_words']:
        config['banned_words'].append(word)
        save_config()
        await update.message.reply_text(f"Added banned word: {word}")
    else:
        await update.message.reply_text("This word is already banned.")

async def remove_banned_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a banned word."""
    if update.effective_user.id != config['owner_id']:
        return
    if not context.args:
        await update.message.reply_text("Please provide a word to unban.")
        return
    word = ' '.join(context.args)
    if word in config['banned_words']:
        config['banned_words'].remove(word)
        save_config()
        await update.message.reply_text(f"Removed banned word: {word}")
    else:
        await update.message.reply_text("Word not found in banned list.")

def main():
    """Start the bot."""
    # Load configuration
    load_config()
    
    if not config['token']:
        print("Please set up your bot token in config.json")
        return
    
    # Create the Application
    application = Application.builder().token(config['token']).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addspam", add_spam_pattern))
    application.add_handler(CommandHandler("removespam", remove_spam_pattern))
    application.add_handler(CommandHandler("listspam", list_spam_patterns))
    application.add_handler(CommandHandler("addword", add_banned_word))
    application.add_handler(CommandHandler("removeword", remove_banned_word))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()