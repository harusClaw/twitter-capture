#!/usr/bin/env python3
"""
Telegram Bot for Twitter Media Extraction

Extracts images, GIFs, and videos from tweets and sends them to Telegram.
"""

import os
import re
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import playwright for scraping
from playwright.async_api import async_playwright

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def is_twitter_url(text: str) -> bool:
    """Check if text contains a Twitter/X URL."""
    twitter_domains = ["twitter.com/", "x.com/", "www.twitter.com/", "www.x.com/"]
    return any(domain in text for domain in twitter_domains)


def extract_twitter_url(text: str) -> str | None:
    """Extract Twitter URL from text."""
    pattern = r'https?://(?:www\.)?(?:twitter|x)\.com/[^\s]+'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None


async def extract_media_from_tweet(url: str) -> dict:
    """
    Extract media from a tweet using Playwright.
    Returns dict with user info, text, and media files.
    """
    # Convert to fixupx.com for better scraping
    fixupx_url = url.replace("twitter.com", "fixupx.com").replace("x.com", "fixupx.com")
    
    result = {
        "user_name": "@unknown",
        "user_handle": "@unknown",
        "text": "",
        "media_files": [],
        "error": None
    }
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate and wait for content
            await page.goto(fixupx_url, wait_until='domcontentloaded', timeout=15000)
            await page.wait_for_selector('article[role="article"]', timeout=10000)
            
            # Extract user info using data-testid (most reliable)
            try:
                # Try data-testid="User-Name" first (fixupx specific)
                user_name_elem = await page.query_selector('[data-testid="User-Name"]')
                if user_name_elem:
                    spans = await user_name_elem.query_selector_all('span')
                    texts = []
                    for span in spans:
                        text = await span.text_content()
                        if text and text.strip():
                            texts.append(text.strip())
                    
                    # Extract name and handle from texts
                    # Usually: [name, name, '', '@handle'] or [name, '@handle']
                    if texts:
                        result["user_name"] = texts[0]
                        for text in texts:
                            if text.startswith('@'):
                                result["user_handle"] = text
                                break
                        
                        # Fallback: if no @handle found, derive from URL
                        if result["user_handle"] == "@unknown":
                            url_match = re.search(r'/status/(\d+)', fixupx_url)
                            if url_match:
                                # Try to get handle from page URL or first link
                                links = await page.query_selector_all('article a[href^="/"]')
                                for link in links:
                                    href = await link.get_attribute('href')
                                    if href and len(href.split('/')) == 2 and not href.startswith('/status'):
                                        result["user_handle"] = href.strip('/')
                                        break
            except Exception as e:
                logger.warning(f"User extraction error: {e}")
            
            # Extract tweet text
            try:
                text_divs = await page.query_selector_all('article div[lang]')
                if text_divs:
                    spans = await text_divs[0].query_selector_all('span')
                    texts = []
                    for span in spans:
                        text = await span.text_content()
                        if text:
                            texts.append(text.strip())
                    result["text"] = ' '.join(texts)
            except Exception as e:
                logger.warning(f"Text extraction error: {e}")
            
            # Extract media files (images/videos)
            try:
                # Extract images
                imgs = await page.query_selector_all('article img')
                for img in imgs:
                    src = await img.get_attribute('src')
                    alt = await img.get_attribute('alt')
                    
                    if not src:
                        continue
                    
                    # Check if this is a GIF (tweet_video_thumb)
                    gif_match = re.search(r'tweet_video(?:_thumb)?\/([a-zA-Z0-9_-]+)(?:\.jpg|\.mp4|\.gif)?', src)
                    if gif_match:
                        video_id = gif_match.group(1)
                        mp4_url = f"https://video.twimg.com/tweet_video/{video_id}.mp4"
                        # Check if already added
                        if not any(m["url"] == mp4_url for m in result["media_files"]):
                            result["media_files"].append({"type": "video", "url": mp4_url})
                        continue  # Skip adding as photo
                    
                    # Filter: Only keep actual tweet media
                    # Skip: avatars, emojis, icons, VIDEO THUMBNAILS
                    if 'profile_images' in src:
                        continue  # Skip avatar
                    if '/emoji/' in src:
                        continue  # Skip emojis
                    if 'abs-0.twimg.com' in src and 'emoji' not in src:
                        continue  # Skip other abs images
                    if 'amplify_video_thumb' in src or 'video_thumb' in src:
                        continue  # Skip video thumbnails (they belong to videos)
                    if '_normal.' in src:
                        continue  # Skip small profile images
                    
                    # Keep: pbs.twimg.com/media (actual tweet images)
                    if 'pbs.twimg.com/media' in src:
                        # Convert to full size
                        full_size = src.replace('&name=small', '&name=4096x4096').replace('&name=medium', '&name=4096x4096')
                        if '&name=' not in full_size:
                            full_size += '&name=4096x4096'
                        result["media_files"].append({"type": "photo", "url": full_size})
                    elif 'pbs.twimg.com' in src and 'tweet_video' not in src:
                        result["media_files"].append({"type": "photo", "url": src})
                
                # Extract videos and GIFs from video tags
                videos = await page.query_selector_all('article video')
                for video in videos:
                    # Try multiple sources
                    src = await video.get_attribute('src')
                    if not src:
                        # Look for <source> elements
                        sources = await video.query_selector_all('source')
                        for source in sources:
                            src = await source.get_attribute('src')
                            if src:
                                break
                    
                    if not src:
                        # Try data-src or other attributes
                        src = await video.get_attribute('data-src')
                    
                    if src and 'video.twimg.com' in src:
                        result["media_files"].append({"type": "video", "url": src})
                
                # Also look for video URLs in data attributes
                all_elements = await page.query_selector_all('article [data-video-url]')
                for elem in all_elements:
                    video_url = await elem.get_attribute('data-video-url')
                    if video_url and 'video.twimg.com' in video_url:
                        # Check if already added
                        if not any(m["url"] == video_url for m in result["media_files"]):
                            result["media_files"].append({"type": "video", "url": video_url})
                        
            except Exception as e:
                logger.warning(f"Media extraction error: {e}")
            
            await browser.close()
            
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Extraction failed: {e}")
    
    return result


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
        f"🔍 Extracting media from:\n{url}"
    )
    
    try:
        # Extract media
        data = await extract_media_from_tweet(url)
        
        if data["error"]:
            await status_msg.edit_text(f"❌ Error: {data['error']}")
            return
        
        if not data["media_files"]:
            await status_msg.edit_text("❌ No media found in this tweet")
            return
        
        # Prepare caption
        caption = f"📸 Tweet from {data['user_name']} ({data['user_handle']})\n\n"
        if data["text"]:
            caption += f"{data['text']}\n\n"
        caption += f"🔗 {url}"
        
        # Separate photos and videos
        photos = [m for m in data["media_files"] if m["type"] == "photo"]
        videos = [m for m in data["media_files"] if m["type"] == "video"]
        
        # Send media
        if videos:
            # Send videos first (each as separate message)
            for i, video in enumerate(videos):
                video_caption = caption if i == 0 else None
                try:
                    await update.message.reply_video(
                        video=video["url"],
                        caption=video_caption
                    )
                except Exception as e:
                    logger.warning(f"Video send failed, sending as document: {e}")
                    await update.message.reply_document(
                        document=video["url"],
                        caption=video_caption
                    )
        
        if photos:
            if len(photos) == 1:
                # Single photo
                photo_caption = caption if not videos else None
                await update.message.reply_photo(
                    photo=photos[0]["url"],
                    caption=photo_caption
                )
            else:
                # Multiple photos - send as album
                from telegram import InputMediaPhoto
                media_group = []
                for i, photo in enumerate(photos):
                    if i == 0 and not videos:
                        media_group.append(InputMediaPhoto(media=photo["url"], caption=caption))
                    elif i == 0 and videos:
                        media_group.append(InputMediaPhoto(media=photo["url"]))
                    else:
                        media_group.append(InputMediaPhoto(media=photo["url"]))
                
                try:
                    await update.message.reply_media_group(media=media_group)
                except Exception as e:
                    logger.warning(f"Album send failed, sending individually: {e}")
                    # Fallback: send each photo separately
                    for i, photo in enumerate(photos):
                        photo_caption = caption if i == 0 else None
                        await update.message.reply_photo(
                            photo=photo["url"],
                            caption=photo_caption
                        )
        
        # Delete status message
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error sending media: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 Hi! I'm a Twitter Media Extraction bot.\n\n"
        "📝 Just send me a Twitter/X URL and I'll extract all images and videos!\n\n"
        "Example:\n"
        "https://twitter.com/username/status/1234567890"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "📖 **How to use:**\n\n"
        "1️⃣ Send me a Twitter/X URL\n"
        "2️⃣ I'll extract all images, GIFs, and videos\n"
        "3️⃣ Media is sent directly to you!\n\n"
        "**Features:**\n"
        "✅ Extracts all images from tweets\n"
        "✅ Supports multiple images (sent as album)\n"
        "✅ Full resolution downloads\n"
        "✅ No watermarks\n\n"
        "**Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help"
    )


def main():
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        print("Error: Please set TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_twitter_url))
    
    # Start the bot
    logger.info("Starting media extraction bot...")
    print("🤖 Twitter Media Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import sys
    main()
