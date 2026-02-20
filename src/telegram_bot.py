#!/usr/bin/env python3
"""
Twitter to Telegram Message Bot
Sends tweet content as native Telegram messages with media.
No image generation - just direct media and text!
"""

import os
import sys
import logging
import re
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright
import requests
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def download_file(url: str) -> bytes | None:
    """Download a file from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        logger.warning(f"Failed to download {url}: {e}")
    return None


async def extract_tweet_data(url: str) -> dict | None:
    """
    Extract tweet data from fixupx.com.
    
    Returns dict with:
    - username: Display name
    - handle: @username
    - avatar_url: Profile picture URL
    - text: Tweet text
    - media_urls: List of image/video URLs
    - timestamp: Tweet time
    - original_url: Original tweet URL
    """
    browser = None
    try:
        # Convert to fixupx.com URL
        fx_url = url.replace('twitter.com', 'fixupx.com').replace('x.com', 'fixupx.com')
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        # Navigate and wait for DOM
        await page.goto(fx_url, wait_until='domcontentloaded', timeout=30000)
        
        # Wait for tweet article
        try:
            await page.wait_for_selector('article[role="article"]', timeout=10000)
        except:
            logger.warning("Tweet article not found")
            return None
        
        # Extract tweet data
        tweet_data = await page.evaluate('''() => {
            const article = document.querySelector('article[role="article"]');
            if (!article) return null;
            
            // Get avatar
            const avatar = article.querySelector('img[src*="profile_images"]');
            
            // Get username and handle
            let username = 'Unknown';
            let handle = '@unknown';
            
            // Use data-testid="User-Name" element
            const nameElement = article.querySelector('[data-testid="User-Name"]');
            if (nameElement) {
                const spans = Array.from(nameElement.querySelectorAll('span'));
                if (spans.length >= 2) {
                    username = spans[0].textContent.trim() || spans[1].textContent.trim() || username;
                    for (const span of spans) {
                        const text = span.textContent.trim();
                        if (text.startsWith('@')) {
                            handle = text;
                            break;
                        }
                    }
                }
            }
            
            // Fallback to link analysis
            if (username === 'Unknown' || handle === '@unknown') {
                const allLinks = Array.from(article.querySelectorAll('a[href*="/"]'));
                let foundUserLink = false;
                
                for (const link of allLinks) {
                    const href = link.getAttribute('href') || '';
                    
                    if (href.includes('/status/') || 
                        href.includes('/hashtag/') || 
                        href.includes('/media/') ||
                        href.includes('/photo/') ||
                        href.includes('/analytics') ||
                        link.querySelector('img')) {
                        continue;
                    }
                    
                    const text = link.textContent.trim();
                    
                    if (!foundUserLink && text.length > 0 && text.length < 50 && !text.startsWith('@')) {
                        username = text;
                        foundUserLink = true;
                    } else if (foundUserLink && text.startsWith('@') && text.length < 20) {
                        handle = text;
                        break;
                    }
                }
            }
            
            // Extract from URL if all else fails
            if (handle === '@unknown') {
                const urlMatch = window.location.href.match(/fixupx\\.com\\/([^\\/]+)/);
                if (urlMatch && urlMatch[1]) {
                    handle = '@' + urlMatch[1];
                    if (username === 'Unknown') {
                        username = urlMatch[1];
                    }
                }
            }
            
            // Get tweet text
            let text = '';
            const textContainer = article.querySelector('div[lang]');
            if (textContainer) {
                const textSpans = textContainer.querySelectorAll('span');
                if (textSpans.length > 0) {
                    text = Array.from(textSpans)
                        .map(span => span.textContent)
                        .join('')
                        .trim();
                } else {
                    text = textContainer.textContent.trim();
                }
            }
            
            // Fallback for text
            if (!text || text.length < 10) {
                const allSpans = Array.from(article.querySelectorAll('span'));
                const contentSpans = allSpans.filter(span => {
                    const txt = span.textContent.trim();
                    return txt.length > 20 && 
                           !txt.startsWith('@') && 
                           !txt.includes('·') &&
                           !txt.includes('http') &&
                           !txt.includes('reply') &&
                           !txt.includes('retweet') &&
                           !txt.includes('like');
                });
                if (contentSpans.length > 0) {
                    text = contentSpans[0].textContent.trim();
                }
            }
            
            // Get media images
            const mediaImgs = Array.from(article.querySelectorAll('img[src*="media"]'))
                .map(img => img.src)
                .filter(src => src && src.length > 0)
                .slice(0, 10);
            
            // Get video if present
            const videoElement = article.querySelector('video[src]');
            const video_url = videoElement ? videoElement.src : null;
            
            // Get timestamp
            const timeElement = article.querySelector('time');
            const timestamp = timeElement ? timeElement.textContent.trim() : new Date().toLocaleString();
            
            return {
                avatar_url: avatar ? avatar.src : null,
                username: username,
                handle: handle,
                text: text,
                media_urls: mediaImgs,
                video_url: video_url,
                timestamp: timestamp,
                original_url: window.location.href
            };
        }''')
        
        await browser.close()
        await playwright.stop()
        
        if tweet_data:
            logger.info(f"Extracted tweet: {tweet_data.get('username')} ({tweet_data.get('handle')})")
            return tweet_data
        
        logger.warning(f"No tweet data extracted from {fx_url}")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting tweet data: {e}")
        return None
    finally:
        if browser:
            try:
                await browser.close()
            except:
                pass


async def handle_twitter_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages containing Twitter URLs."""
    text = update.message.text if update.message else ""
    
    # Check if message contains a Twitter/X URL
    twitter_urls = []
    for word in text.split():
        if 'twitter.com' in word or 'x.com' in word:
            url = word.strip('<>()')
            if url.startswith('http'):
                twitter_urls.append(url)
    
    if not twitter_urls:
        return
    
    # Process each Twitter URL
    for url in twitter_urls:
        logger.info(f"Processing Twitter URL: {url}")
        
        # Send "processing" message
        processing_msg = await update.message.reply_text("🔍 Extracting tweet...")
        
        try:
            # Extract tweet data
            tweet_data = await extract_tweet_data(url)
            
            if not tweet_data:
                await update.message.reply_text(
                    f"❌ Failed to extract tweet data.\n\n"
                    f"This might be due to:\n"
                    f"• Private account\n"
                    f"• Deleted tweet\n"
                    f"• Network issues\n\n"
                    f"URL: {url}"
                )
                continue
            
            # Build caption
            caption_parts = []
            
            # Add user info
            username = tweet_data.get('username', 'Unknown')
            handle = tweet_data.get('handle', '@unknown')
            caption_parts.append(f"📱 **Tweet from {username}** {handle}")
            
            # Add tweet text
            tweet_text = tweet_data.get('text', '')
            if tweet_text:
                # Truncate if too long (Telegram limit is 4096)
                if len(tweet_text) > 4000:
                    tweet_text = tweet_text[:3997] + "..."
                caption_parts.append(f"\n{tweet_text}")
            
            # Add timestamp
            timestamp = tweet_data.get('timestamp', '')
            if timestamp:
                caption_parts.append(f"\n\n⏰ {timestamp}")
            
            # Add original link
            caption_parts.append(f"\n🔗 {url}")
            
            caption = "\n".join(caption_parts)
            
            # Send media
            media_urls = tweet_data.get('media_urls', [])
            video_url = tweet_data.get('video_url')
            
            if video_url:
                # Send video
                video_data = await download_file(video_url)
                if video_data:
                    await update.message.reply_video(
                        video=video_data,
                        caption=caption,
                        parse_mode='Markdown'
                    )
                else:
                    # Fallback to text message
                    await update.message.reply_text(
                        caption,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
            elif media_urls:
                # Send images
                if len(media_urls) == 1:
                    # Single image
                    image_data = await download_file(media_urls[0])
                    if image_data:
                        await update.message.reply_photo(
                            photo=image_data,
                            caption=caption,
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text(
                            caption,
                            parse_mode='Markdown',
                            disable_web_page_preview=True
                        )
                else:
                    # Multiple images - send as album
                    image_data_list = []
                    for i, media_url in enumerate(media_urls[:10]):
                        image_data = await download_file(media_url)
                        if image_data:
                            if i == 0:
                                # First image gets the caption
                                image_data_list.append({
                                    'type': 'photo',
                                    'media': image_data,
                                    'caption': caption,
                                    'parse_mode': 'Markdown'
                                })
                            else:
                                image_data_list.append({
                                    'type': 'photo',
                                    'media': image_data
                                })
                    
                    if image_data_list:
                        await update.message.reply_media_group(
                            media=image_data_list
                        )
                    else:
                        # Fallback to text
                        await update.message.reply_text(
                            caption,
                            parse_mode='Markdown',
                            disable_web_page_preview=True
                        )
            else:
                # No media, just send text
                await update.message.reply_text(
                    caption,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            # Delete processing message
            try:
                await processing_msg.delete()
            except:
                pass


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    await update.message.reply_text(
        "👋 Hi! I'm a Twitter to Telegram bot.\n\n"
        "📱 Just send me a Twitter/X URL and I'll forward the tweet content!\n\n"
        "Examples:\n"
        "• https://twitter.com/username/status/123456\n"
        "• https://x.com/username/status/123456\n\n"
        "✨ Features:\n"
        "• Tweet text with emojis\n"
        "• Images & videos as native media\n"
        "• No login walls!\n"
        "• Fast & simple"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    await update.message.reply_text(
        "📖 How to use:\n\n"
        "1. Send any Twitter/X URL\n"
        "2. Wait a few seconds\n"
        "3. Receive the tweet content!\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/ping - Check if bot is alive\n\n"
        "💡 Tips:\n"
        "• Works with both twitter.com and x.com\n"
        "• Handles multiple URLs in one message\n"
        "• Private accounts won't work"
    )


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ping command."""
    await update.message.reply_text("🏓 Pong! Bot is running! ✅")


def main() -> None:
    """Start the bot."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        print("Error: Please set TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)
    
    logger.info("Starting Twitter to Telegram Bot...")
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_twitter_url
        )
    )
    
    logger.info("Bot is running!")
    print("✅ Bot is running! Send Twitter URLs to get tweet content! 📱")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
