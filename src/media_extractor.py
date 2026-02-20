#!/usr/bin/env python3
"""
Twitter Media Extractor Bot
Simple bot that extracts and sends media (images/GIFs) from Twitter/X URLs
"""

import os
import sys
import re
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

import requests
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set")
    print("Error: TELEGRAM_BOT_TOKEN not set")
    sys.exit(1)

# Media directory
MEDIA_DIR = Path("/home/openclaw/.nanobot/media")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def is_twitter_url(text: str) -> bool:
    """Check if text contains a Twitter/X URL"""
    patterns = [
        r'(https?://)?(www\.)?(twitter\.com|x\.com)/\w+/status/\d+',
        r'(https?://)?(www\.)?(vxtwitter\.com|fixupx\.com)/\w+/status/\d+',
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def extract_twitter_url(text: str) -> str | None:
    """Extract Twitter/X URL from text"""
    patterns = [
        r'(https?://(?:www\.)?(?:twitter\.com|x\.com|vxtwitter\.com|fixupx\.com)/\w+/status/\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(1)
            # Normalize to x.com
            url = url.replace('twitter.com', 'x.com')
            url = url.replace('vxtwitter.com', 'fixupx.com')
            return url
    return None


async def extract_media_from_tweet(tweet_url: str) -> list[dict]:
    """
    Extract media from a tweet using fixupx.com
    Returns list of dicts with 'type' and 'url' keys
    """
    media_list = []
    
    # Convert to fixupx URL
    fixupx_url = tweet_url.replace('x.com', 'fixupx.com')
    fixupx_url = fixupx_url.replace('twitter.com', 'fixupx.com')
    fixupx_url = fixupx_url.replace('vxtwitter.com', 'fixupx.com')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        try:
            await page.goto(fixupx_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector("article[role='article']", timeout=10000)
            await asyncio.sleep(2)  # Let images load
            
            # Find all media elements
            # Look for images in the article
            images = await page.query_selector_all("article[role='article'] img[src*='media']")
            
            for img in images:
                src = await img.get_attribute("src")
                if src and src.startswith("http"):
                    # Check if it's a video thumbnail or actual image
                    # Twitter video thumbnails contain "video_thumb"
                    if "video_thumb" in src:
                        # Try to find the actual video
                        continue
                    else:
                        # It's an image - get the best quality
                        # Remove size parameters to get original
                        original_url = src.split("?")[0] + "?name=4096x4096"
                        media_list.append({"type": "photo", "url": original_url})
            
            # Look for video elements
            videos = await page.query_selector_all("article[role='article'] video")
            for video in videos:
                src = await video.get_attribute("src")
                if src and src.startswith("http"):
                    media_list.append({"type": "video", "url": src})
            
            # Also check for GIF elements (they're usually videos in disguise)
            gifs = await page.query_selector_all("article[role='article'] img[src*='gif']")
            for gif in gifs:
                src = await gif.get_attribute("src")
                if src and src.startswith("http"):
                    media_list.append({"type": "gif", "url": src})
            
            # Deduplicate media
            seen_urls = set()
            unique_media = []
            for media in media_list:
                if media["url"] not in seen_urls:
                    seen_urls.add(media["url"])
                    unique_media.append(media)
            
            return unique_media
            
        except Exception as e:
            print(f"Error extracting media: {e}")
            return []
        finally:
            await browser.close()


async def download_media(url: str, filename: str) -> str | None:
    """Download media to temp file, return path or None"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        filepath = MEDIA_DIR / filename
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        return str(filepath)
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    text = update.message.text if update.message.text else ""
    
    if not is_twitter_url(text):
        return
    
    tweet_url = extract_twitter_url(text)
    if not tweet_url:
        await update.message.reply_text("❌ Could not extract Twitter URL from message")
        return
    
    await update.message.reply_text(f"🔍 Extracting media from:\n{tweet_url}")
    
    # Extract media
    media_list = await extract_media_from_tweet(tweet_url)
    
    if not media_list:
        await update.message.reply_text("❌ No media found in this tweet")
        return
    
    await update.message.reply_text(f"✅ Found {len(media_list)} media item(s)")
    
    # Send each media
    for i, media in enumerate(media_list, 1):
        media_type = media["type"]
        media_url = media["url"]
        
        # Download media
        filename = f"twitter_media_{update.message.message_id}_{i}"
        if media_type == "photo":
            filename += ".jpg"
        elif media_type == "gif":
            filename += ".gif"
        elif media_type == "video":
            filename += ".mp4"
        
        filepath = await download_media(media_url, filename)
        
        if not filepath:
            await update.message.reply_text(f"❌ Failed to download media {i}")
            continue
        
        # Send to Telegram
        try:
            if media_type in ["photo", "gif"]:
                await update.message.reply_photo(photo=open(filepath, "rb"))
            elif media_type == "video":
                await update.message.reply_video(video=open(filepath, "rb"))
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to send media {i}: {e}")
        finally:
            # Clean up temp file
            try:
                os.remove(filepath)
            except:
                pass


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🎯 **Twitter Media Extractor**\n\n"
        "Send me any Twitter/X URL and I'll extract the images, GIFs, and videos!\n\n"
        "Examples:\n"
        "• https://x.com/user/status/123456\n"
        "• https://twitter.com/user/status/123456"
    )


def main():
    """Main bot loop"""
    logger.info("Starting Twitter Media Extractor Bot...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is running! Press Ctrl+C to stop.")
    print("🎯 Twitter Media Extractor Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
