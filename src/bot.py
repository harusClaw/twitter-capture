#!/usr/bin/env python3
"""
Twitter Media Extractor - Telegram Bot
Extracts and sends media from Twitter/X URLs
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


async def extract_tweet_data(url: str) -> dict | None:
    """
    Extract tweet data from fixupx.com.
    
    Returns dict with:
    - username: Display name
    - handle: @username
    - text: Tweet text
    - media_urls: List of image/video URLs
    - timestamp: Tweet time
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
            
            // Get username and handle - multiple methods
            let username = 'Unknown';
            let handle = '@unknown';
            
            // Method 1: data-testid="User-Name" (most reliable)
            const nameElement = article.querySelector('[data-testid="User-Name"]');
            if (nameElement) {
                const spans = Array.from(nameElement.querySelectorAll('span'));
                const texts = spans.map(s => s.textContent.trim()).filter(t => t.length > 0);
                
                // Find display name (usually first non-@ text)
                for (const text of texts) {
                    if (!text.startsWith('@') && text.length > 0) {
                        username = text;
                        break;
                    }
                }
                
                // Find handle (starts with @)
                for (const text of texts) {
                    if (text.startsWith('@')) {
                        handle = text;
                        break;
                    }
                }
            }
            
            // Method 2: Fallback - look for links to user profiles
            if (username === 'Unknown' || handle === '@unknown') {
                const userLinks = Array.from(article.querySelectorAll('a[href^="/"]'))
                    .filter(a => {
                        const href = a.getAttribute('href');
                        // Exclude hashtags, status links, and avatar links
                        return href && 
                               !href.startsWith('/hashtag/') && 
                               !href.includes('/status/') &&
                               !href.includes('/photo/');
                    });
                
                if (userLinks.length >= 1) {
                    // First link is usually display name
                    const displayName = userLinks[0].textContent.trim();
                    if (displayName && displayName.length > 0 && !displayName.startsWith('@')) {
                        username = displayName;
                    }
                    
                    // Second link or same link might have handle
                    if (userLinks.length >= 2) {
                        const handleText = userLinks[1].textContent.trim();
                        if (handleText && handleText.startsWith('@')) {
                            handle = handleText;
                        }
                    }
                    
                    // Derive handle from URL if not found
                    if (handle === '@unknown') {
                        const href = userLinks[0].getAttribute('href');
                        if (href && href.startsWith('/') && !href.includes('/')) {
                            handle = '@' + href.substring(1);
                        }
                    }
                }
            }
            
            // Method 3: Extract from URL as last resort
            if (handle === '@unknown') {
                const urlMatch = window.location.pathname.match(/\/([a-zA-Z0-9_]+)\/status\//);
                if (urlMatch) {
                    handle = '@' + urlMatch[1];
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
            
            // Get media images - exclude video thumbnails but handle GIFs separately
            const mediaImgs = Array.from(article.querySelectorAll('img[src*="pbs.twimg.com"]'))
                .map(img => img.src)
                .filter(src => src && src.length > 0)
                .filter(src => !src.includes('profile_images')) // Exclude avatars
                .filter(src => !src.includes('amplify_video_thumb')) // Exclude video thumbnails
                .filter(src => !src.includes('/emoji/')) // Exclude emojis
                .filter(src => !src.includes('_normal.')) // Exclude normal-sized profile images
                // Keep GIF thumbnails - they'll be converted to videos later
                .slice(0, 4);
            
            // Get video URLs - multiple methods
            const videos = [];
            
            // Method 1: <video> with <source> children
            const videoElements = article.querySelectorAll('video');
            videoElements.forEach(video => {
                // Try direct src
                if (video.src) videos.push(video.src);
                // Try <source> elements
                const sources = video.querySelectorAll('source');
                sources.forEach(source => {
                    if (source.src) videos.push(source.src);
                });
            });
            
            // Method 2: Look for video.twimg.com URLs in any element (includes GIFs)
            const allElements = article.querySelectorAll('*');
            allElements.forEach(el => {
                const src = el.getAttribute('src');
                if (src && src.includes('video.twimg.com') && !videos.includes(src)) {
                    videos.push(src);
                }
                const dataSrc = el.getAttribute('data-src');
                if (dataSrc && dataSrc.includes('video.twimg.com') && !videos.includes(dataSrc)) {
                    videos.push(dataSrc);
                }
            });
            
            // Method 3: Look for tweet_video URLs (GIFs) - check img tags and convert to MP4
            const gifImgElements = article.querySelectorAll('img[src*="tweet_video"]');
            gifImgElements.forEach(img => {
                let src = img.getAttribute('src') || img.getAttribute('data-src');
                if (src && src.includes('tweet_video') && !videos.includes(src)) {
                    // Convert GIF thumb URL to actual video URL
                    // e.g., https://pbs.twimg.com/tweet_video_thumb/ABC123.jpg -> https://video.twimg.com/tweet_video/ABC123.mp4
                    // Match both: tweet_video_thumb/ID.jpg and tweet_video/ID.mp4
                    const match = src.match(/tweet_video(?:_thumb)?\/([a-zA-Z0-9_-]+)(?:\.jpg|\.mp4|\.gif)?/);
                    if (match) {
                        const videoId = match[1];
                        const videoUrl = `https://video.twimg.com/tweet_video/${videoId}.mp4`;
                        if (!videos.includes(videoUrl)) {
                            videos.push(videoUrl);
                        }
                    } else {
                        // Fallback: use src directly if it looks like a video URL
                        if (src.includes('video.twimg.com')) {
                            videos.push(src);
                        }
                    }
                }
            });
            
            // Method 4: Look for data-video-url or similar attributes
            const videoContainers = article.querySelectorAll('[data-video-url], [data-url*="video"]');
            videoContainers.forEach(el => {
                const url = el.getAttribute('data-video-url') || el.getAttribute('data-url');
                if (url && url.includes('video.twimg.com') && !videos.includes(url)) {
                    videos.push(url);
                }
            });
            
            // Remove duplicates
            const uniqueVideos = [...new Set(videos)];
            
            // Get timestamp
            const timeElement = article.querySelector('time');
            const timestamp = timeElement ? timeElement.textContent.trim() : new Date().toLocaleString();
            
            return {
                username: username,
                handle: handle,
                text: text,
                media_urls: mediaImgs,
                video_urls: uniqueVideos,
                timestamp: timestamp
            };
        }''')
        
        await browser.close()
        await playwright.stop()
        
        if tweet_data:
            logger.info(f"Extracted tweet: {tweet_data.get('username')} - Text: {tweet_data.get('text', '')[:50]}...")
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


async def download_file(url: str) -> BytesIO | None:
    """Download a file from URL and return as BytesIO."""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception as e:
        logger.warning(f"Failed to download {url}: {e}")
    return None


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
        processing_msg = await update.message.reply_text("🔍 Extracting media from tweet...")
        
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
            if tweet_data.get('username'):
                caption_parts.append(f"👤 {tweet_data['username']} ({tweet_data.get('handle', '@unknown')})")
            if tweet_data.get('text'):
                caption_parts.append(f"\n📝 {tweet_data['text']}")
            if tweet_data.get('timestamp'):
                caption_parts.append(f"\n⏰ {tweet_data['timestamp']}")
            caption_parts.append(f"\n\n🔗 {url}")
            
            caption = ''.join(caption_parts)
            
            # Get all media URLs
            all_media = tweet_data.get('media_urls', []) + tweet_data.get('video_urls', [])
            
            if not all_media:
                # No media, just send text
                await update.message.reply_text(caption)
            elif len(all_media) == 1:
                # Single media - send as photo, video, or document
                media_url = all_media[0]
                logger.info(f"Downloading single media: {media_url}")
                
                file_bytes = await download_file(media_url)
                if file_bytes:
                    file_bytes.seek(0)
                    
                    # Detect if it's a video
                    is_video = 'video.twimg.com' in media_url or media_url.endswith('.mp4')
                    
                    if is_video:
                        # Send as video
                        try:
                            await update.message.reply_video(video=file_bytes, caption=caption)
                        except Exception as e:
                            logger.warning(f"Video send failed, sending as document: {e}")
                            file_bytes.seek(0)
                            await update.message.reply_document(document=file_bytes, caption=caption, filename='video.mp4')
                    else:
                        # Send as photo
                        try:
                            await update.message.reply_photo(photo=file_bytes, caption=caption)
                        except Exception as e:
                            # If photo fails, send as document
                            logger.warning(f"Photo send failed, sending as document: {e}")
                            file_bytes.seek(0)
                            await update.message.reply_document(document=file_bytes, caption=caption, filename='media.jpg')
                else:
                    await update.message.reply_text(f"❌ Failed to download media.\n\n{caption}")
            else:
                # Multiple media - send as media group
                logger.info(f"Downloading {len(all_media)} media files")
                
                media_group = []
                for i, media_url in enumerate(all_media[:4]):  # Max 4 for Telegram album
                    file_bytes = await download_file(media_url)
                    if file_bytes:
                        file_bytes.seek(0)
                        
                        # Detect if it's a video
                        is_video = 'video.twimg.com' in media_url or media_url.endswith('.mp4')
                        
                        if is_video:
                            from telegram import InputMediaVideo
                            if i == 0:
                                media_group.append(InputMediaVideo(media=file_bytes, caption=caption))
                            else:
                                media_group.append(InputMediaVideo(media=file_bytes))
                        else:
                            from telegram import InputMediaPhoto
                            if i == 0:
                                media_group.append(InputMediaPhoto(media=file_bytes, caption=caption))
                            else:
                                media_group.append(InputMediaPhoto(media=file_bytes))
                
                if media_group:
                    try:
                        await update.message.reply_media_group(media=media_group)
                    except Exception as e:
                        logger.error(f"Media group failed: {e}")
                        # Fallback: send each media separately
                        for i, media_url in enumerate(all_media[:4]):
                            file_bytes = await download_file(media_url)
                            if file_bytes:
                                file_bytes.seek(0)
                                is_video = 'video.twimg.com' in media_url or media_url.endswith('.mp4')
                                if is_video:
                                    await update.message.reply_video(video=file_bytes, caption=f"📹 {i+1}/{len(all_media)}\n\n{caption}")
                                else:
                                    await update.message.reply_photo(photo=file_bytes, caption=f"📷 {i+1}/{len(all_media)}\n\n{caption}")
                else:
                    await update.message.reply_text(f"❌ Failed to download any media.\n\n{caption}")
                
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}", exc_info=True)
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
        "👋 Hi! I'm a Twitter Media Extractor bot.\n\n"
        "📱 Just send me a Twitter/X URL and I'll extract all the images and videos!\n\n"
        "Examples:\n"
        "• https://twitter.com/username/status/123456\n"
        "• https://x.com/username/status/123456\n\n"
        "✨ Features:\n"
        "• Extracts all images (up to 4)\n"
        "• Extracts videos\n"
        "• Shows tweet text with emojis\n"
        "• No login walls!\n"
        "• Multiple images sent as album"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    await update.message.reply_text(
        "📖 How to use:\n\n"
        "1. Send any Twitter/X URL\n"
        "2. Wait a few seconds\n"
        "3. Get all the media files!\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/ping - Check if bot is alive\n\n"
        "💡 Tips:\n"
        "• Works with both twitter.com and x.com\n"
        "• Handles multiple URLs in one message\n"
        "• Private accounts won't work\n"
        "• Multiple images sent as swipeable album"
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
    
    logger.info("Starting Twitter Media Extractor Bot...")
    
    # Build application with proper configuration
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
    
    logger.info("Bot is running! Press Ctrl+C to stop.")
    print("✅ Bot is running! Send Twitter URLs to extract media! 🎨")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
