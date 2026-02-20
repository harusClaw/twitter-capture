#!/usr/bin/env python3
"""
Telegram Bot for Twitter URL to Image Conversion

This bot listens for Twitter URLs and converts them to images.
"""

import os
import sys
import subprocess
import tempfile
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
TWITTER_CAPTURE_BIN = os.getenv(
    "TWITTER_CAPTURE_BIN", 
    "/home/openclaw/.nanobot/workspace/projects/twitter-capture/zig-out/bin/twitter-capture"
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def is_twitter_url(text: str) -> bool:
    """Check if text contains a Twitter/X URL."""
    twitter_domains = [
        "twitter.com/",
        "x.com/",
        "www.twitter.com/",
        "www.x.com/",
        "mobile.twitter.com/",
    ]
    return any(domain in text for domain in twitter_domains)


def extract_twitter_url(text: str) -> str | None:
    """Extract Twitter URL from text."""
    import re
    pattern = r'https?://(?:www\.)?(?:twitter|x)\.com/[^\s]+'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


async def capture_tweet(url: str) -> Path | None:
    """
    Capture Twitter URL as image using the Zig tool.
    Returns path to the generated image or None on failure.
    """
    try:
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            output_path = tmp.name
        
        # Run the twitter-capture tool
        cmd = [TWITTER_CAPTURE_BIN, url, output_path]
        logger.info(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            logger.error(f"Capture failed: {result.stderr}")
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
            return None
        
        logger.info(f"Successfully captured: {output_path}")
        return Path(output_path)
        
    except subprocess.TimeoutExpired:
        logger.error("Capture timed out")
        return None
    except Exception as e:
        logger.error(f"Capture error: {e}")
        return None


async def handle_twitter_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages containing Twitter URLs."""
    text = update.message.text if update.message else None
    if not text:
        return
    
    url = extract_twitter_url(text)
    if not url:
        return
    
    # Send "processing" message
    status_msg = await update.message.reply_text(
        "🐦 Capturing tweet... Please wait..."
    )
    
    try:
        # Capture the tweet
        image_path = await capture_tweet(url)
        
        if image_path and image_path.exists():
            # Send the image
            await update.message.reply_photo(
                photo=open(image_path, 'rb'),
                caption=f"📸 Captured from: {url}"
            )
            
            # Clean up temporary file
            image_path.unlink()
            
            # Delete status message
            await status_msg.delete()
        else:
            await status_msg.edit_text(
                "❌ Failed to capture tweet. Make sure the URL is valid and public."
            )
    
    except Exception as e:
        logger.error(f"Error sending image: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 Hi! I'm a Twitter URL to Image bot.\n\n"
        "📝 Just send me a Twitter/X URL and I'll convert it to an image!\n\n"
        "Example:\n"
        "https://twitter.com/username/status/1234567890"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "📖 **How to use:**\n\n"
        "1️⃣ Send me a Twitter/X URL\n"
        "2️⃣ I'll capture it as an image\n"
        "3️⃣ You can then share the image!\n\n"
        "**Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/tweet <url> - Capture a specific tweet\n\n"
        "**Supported URLs:**\n"
        "- twitter.com/*\n"
        "- x.com/*\n"
        "- Mobile URLs"
    )


async def tweet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tweet command."""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a Twitter URL.\n\n"
            "Usage: /tweet https://twitter.com/user/status/123"
        )
        return
    
    url = context.args[0]
    
    # Create a fake message for the handler
    update.message.text = url
    await handle_twitter_url(update, context)


def main():
    """Start the bot."""
    # Check if binary exists
    if not Path(TWITTER_CAPTURE_BIN).exists():
        logger.error(f"Twitter capture binary not found: {TWITTER_CAPTURE_BIN}")
        print(f"Error: Binary not found at {TWITTER_CAPTURE_BIN}")
        print("Please build the project first:")
        print("  cd /home/openclaw/.nanobot/workspace/projects/twitter-capture")
        print("  zig build -Doptimize=ReleaseFast")
        sys.exit(1)
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tweet", tweet_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_twitter_url))
    
    # Start the bot
    logger.info("Starting bot...")
    print("🤖 Twitter Capture Bot is running...")
    print(f"Binary: {TWITTER_CAPTURE_BIN}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
