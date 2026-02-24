#!/usr/bin/env python3
"""
Twitter Capture Telegram Bot

Extracts images, videos, and GIFs from Twitter/X URLs and sends them to Telegram.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from io import BytesIO

from .extractor import extract_tweet_data

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def download_file(url: str) -> BytesIO | None:
    """Download a file from URL and return as BytesIO."""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception as e:
        logger.warning(f"Failed to download {url}: {e}")
    return None


async def debug_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Debug handler to log all message details including media types."""
    msg = update.message
    if not msg:
        return
    
    logger.info("=" * 60)
    logger.info(f"📨 MESSAGE RECEIVED - ID: {msg.message_id}")
    logger.info("=" * 60)
    logger.info(f"📝 Text: {msg.text}")
    logger.info(f"📝 Caption: {msg.caption}")
    logger.info(f"📷 Photo: {bool(msg.photo)} ({len(msg.photo) if msg.photo else 0} sizes)")
    logger.info(f"📄 Document: {bool(msg.document)}")
    logger.info(f"🎬 Video: {bool(msg.video)}")
    logger.info(f"🎬 Animation (GIF): {bool(msg.animation)}")
    logger.info(f"🎤 Voice: {bool(msg.voice)}")
    logger.info(f"🎵 Audio: {bool(msg.audio)}")
    logger.info(f"🎭 Sticker: {bool(msg.sticker)}")
    logger.info(f"📞 Contact: {bool(msg.contact)}")
    logger.info(f"📍 Location: {bool(msg.location)}")
    logger.info(f"🔗 Media type property: {getattr(msg, 'media_type', 'N/A')}")
    
    # Log file details if document/video
    if msg.document:
        logger.info(f"   └─ Document: {msg.document.file_name} ({msg.document.file_size} bytes)")
    if msg.video:
        logger.info(f"   └─ Video: {msg.video.file_name} ({msg.video.file_size} bytes, {msg.video.duration}s)")
    if msg.animation:
        logger.info(f"   └─ Animation: {msg.animation.file_name} ({msg.animation.file_size} bytes)")
    if msg.photo:
        logger.info(f"   └─ Photo sizes: {[p.file_size for p in msg.photo]}")
    
    logger.info("=" * 60)
    
    # Check if any media is present
    has_media = bool(msg.photo or msg.document or msg.video or msg.animation or msg.voice or msg.audio or msg.sticker)
    
    # If it has Twitter URL, still process it
    if msg.text and ('twitter.com' in msg.text or 'x.com' in msg.text):
        await handle_twitter_url(update, context)
    elif has_media:
        # Send debug info back to user
        debug_info = (
            "🔍 **Media Detected**\n\n"
            f"📷 Photo: {bool(msg.photo)}\n"
            f"📄 Document: {bool(msg.document)}\n"
            f"🎬 Video: {bool(msg.video)}\n"
            f"🎬 GIF: {bool(msg.animation)}\n"
            f"🎤 Voice: {bool(msg.voice)}\n"
            f"🎵 Audio: {bool(msg.audio)}\n"
            f"📝 Caption: {msg.caption or 'None'}\n"
        )
        if msg.document:
            debug_info += f"📁 File: {msg.document.file_name}\n"
        if msg.video:
            debug_info += f"🎬 Video: {msg.video.file_name}\n"
        await update.message.reply_text(debug_info)


async def handle_twitter_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages containing Twitter URLs."""
    text = update.message.text if update.message else ""
    
    # Extract Twitter URLs from message
    twitter_urls = []
    for word in text.split():
        if 'twitter.com' in word or 'x.com' in word:
            url = word.strip('<>()')
            if url.startswith('http'):
                twitter_urls.append(url)
    
    if not twitter_urls:
        return
    
    # Process each URL
    for url in twitter_urls:
        logger.info(f"Processing: {url}")
        
        # Send processing message
        processing_msg = await update.message.reply_text("🔍 Extracting media...")
        
        try:
            # Extract tweet data
            tweet_data = await extract_tweet_data(url)
            
            if not tweet_data:
                await update.message.reply_text(
                    f"❌ Failed to extract tweet data.\n\n"
                    f"Possible reasons:\n"
                    f"• Private account\n"
                    f"• Deleted tweet\n"
                    f"• Network issues\n\n"
                    f"URL: {url}"
                )
                continue
            
            # Check for specific errors
            if tweet_data.get('error'):
                error_type = tweet_data.get('error')
                error_msg = tweet_data.get('message', 'Unknown error')
                
                if error_type == 'sensitive_content':
                    await update.message.reply_text(
                        f"⚠️ **Sensitive Content Detected**\n\n"
                        f"{error_msg}\n\n"
                        f"Unfortunately, tweets with R18/age-restricted content "
                        f"require Twitter login to view, which this bot cannot bypass.\n\n"
                        f"URL: {url}"
                    )
                elif error_type == 'twitter_error':
                    await update.message.reply_text(
                        f"❌ **Twitter Error**\n\n"
                        f"{error_msg}\n\n"
                        f"This usually means:\n"
                        f"• Tweet was deleted\n"
                        f"• Account is private\n"
                        f"• Account was suspended\n"
                        f"• Age verification required\n\n"
                        f"URL: {url}"
                    )
                else:
                    await update.message.reply_text(f"❌ Error: {error_msg}\n\nURL: {url}")
                
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
            
            # Combine all media
            all_media = tweet_data.get('media_urls', []) + tweet_data.get('video_urls', [])
            
            if not all_media:
                await update.message.reply_text(caption)
            elif len(all_media) == 1:
                # Single media
                await _send_single_media(update, all_media[0], caption)
            else:
                # Multiple media - send as album
                await _send_media_album(update, all_media[:4], caption)
                
        except Exception as e:
            logger.error(f"Error processing {url}: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            try:
                await processing_msg.delete()
            except Exception:
                pass


async def _send_single_media(update: Update, media_url: str, caption: str) -> None:
    """Send a single media file."""
    logger.info(f"Downloading: {media_url}")
    file_bytes = await download_file(media_url)
    
    if not file_bytes:
        await update.message.reply_text(f"❌ Failed to download media.\n\n{caption}")
        return
    
    file_bytes.seek(0)
    is_video = 'video.twimg.com' in media_url or media_url.endswith('.mp4')
    
    try:
        if is_video:
            await update.message.reply_video(video=file_bytes, caption=caption)
        else:
            await update.message.reply_photo(photo=file_bytes, caption=caption)
    except Exception as e:
        logger.warning(f"Send failed, trying document: {e}")
        file_bytes.seek(0)
        filename = 'video.mp4' if is_video else 'media.jpg'
        await update.message.reply_document(document=file_bytes, caption=caption, filename=filename)


async def _send_media_album(update: Update, media_urls: list, caption: str) -> None:
    """Send multiple media as an album."""
    logger.info(f"Downloading {len(media_urls)} files for album")
    
    media_group = []
    for i, media_url in enumerate(media_urls):
        file_bytes = await download_file(media_url)
        if not file_bytes:
            continue
        
        file_bytes.seek(0)
        is_video = 'video.twimg.com' in media_url or media_url.endswith('.mp4')
        
        if is_video:
            if i == 0:
                media_group.append(InputMediaVideo(media=file_bytes, caption=caption))
            else:
                media_group.append(InputMediaVideo(media=file_bytes))
        else:
            if i == 0:
                media_group.append(InputMediaPhoto(media=file_bytes, caption=caption))
            else:
                media_group.append(InputMediaPhoto(media=file_bytes))
    
    if not media_group:
        await update.message.reply_text(f"❌ Failed to download any media.\n\n{caption}")
        return
    
    try:
        await update.message.reply_media_group(media=media_group)
    except Exception as e:
        logger.error(f"Album failed, sending individually: {e}")
        # Fallback: send separately
        for i, media_url in enumerate(media_urls):
            file_bytes = await download_file(media_url)
            if file_bytes:
                file_bytes.seek(0)
                is_video = 'video.twimg.com' in media_url or media_url.endswith('.mp4')
                item_caption = f"{i+1}/{len(media_urls)}\n\n{caption}"
                if is_video:
                    await update.message.reply_video(video=file_bytes, caption=item_caption)
                else:
                    await update.message.reply_photo(photo=file_bytes, caption=item_caption)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        "👋 こんにちは！Twitter メディア抽出ボットです。\n\n"
        "📱 Twitter/X の URL を送信するだけで、全ての画像と動画を抽出します！\n\n"
        "📋 **使用例:**\n"
        "• https://twitter.com/username/status/123456\n"
        "• https://x.com/username/status/123456\n\n"
        "✨ **機能:**\n"
        "• 全ての画像を抽出 (最大 4 枚)\n"
        "• 動画と GIF を抽出\n"
        "• ツイートテキストを表示\n"
        "• ログイン不要\n"
        "• 複数画像はアルバムで送信\n"
        "• 最新ガチャバナーも確認可能 (/banners)\n\n"
        "🎮 **対応ゲーム:**\n"
        "• 原神 (Genshin Impact)\n"
        "• 崩壊：スターレイル\n"
        "• 鳴潮 (Wuthering Waves)\n"
        "• 絶区零 (Zenless Zone Zero)\n\n"
        "詳しくは /help をご覧ください！"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        "📖 **使い方:**\n\n"
        "1. Twitter/X の URL を送信\n"
        "2. 数秒待つ\n"
        "3. 全てのメディアファイルを取得！\n\n"
        "📋 **コマンド:**\n"
        "/start - ボットを起動\n"
        "/help - ヘルプを表示\n"
        "/ping - 動作確認\n"
        "/banners - 最新ガチャバナーを表示 (原神/スタレ/鳴潮/絶区零)\n\n"
        "💡 **ヒント:**\n"
        "• twitter.com と x.com の両方に対応\n"
        "• 複数の URL も処理可能\n"
        "• 非公開アカウントは動作しません\n"
        "• /banners で最新バナーを確認できます"
    )


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ping command."""
    await update.message.reply_text("🏓 Pong! Bot is running! ✅")


async def banners_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /banners command - Show latest gacha banners (Japanese)."""
    await update.message.reply_text(
        "🌟 **原神 (Genshin Impact)** バージョン 6.4\n"
        "📅 **次期バージョン:** 2026 年 2 月 25 日〜\n\n"
        "📍 **新キャラクター:**\n"
        "• ヴァルカ (5★) - 新規\n\n"
        "📍 **現在 (v6.3):**\n"
        "• コロンビーナ (5★)\n"
        "• 紫拝、イルガ (新規)\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚂 **崩壊：スターレイル (Honkai: Star Rail)** バージョン 4.0\n\n"
        "📍 **前半** (2/12 〜 3/3):\n"
        "•  Yao Guang (5★, 物理/欢楽) - 新規\n"
        "• 復刻：エヴァーナイト + ヒシリンス + ブラックスワン\n"
        "• 4★: ペラ、 Hanya、清雀\n\n"
        "📍 **後半** (3/3 〜 3/24):\n"
        "• Sparxie (5★, 炎/欢楽) - 新規\n"
        "• 復刻：Cerydra + ラッパ + スパークル\n\n"
        "🎁 **無料 5★ 選択チケット** 配布中！\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌊 **鳴潮 (Wuthering Waves)** バージョン 3.1\n\n"
        "📍 **前半** (2/4 〜 2/26):\n"
        "• Aemeath (5★) - 新規\n"
        "• 復刻：ルパ、チサ\n\n"
        "🎁 **ログインボーナス:** 1600 星音\n"
        "📅 **終了:** 2026 年 2 月 26 日\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📺 **絶区零 (Zenless Zone Zero)**\n\n"
        "📍 **前半** (2/6 〜 3/4 12:59):\n"
        "• 千夏 (5★) - 「想いが織りなす歌」\n\n"
        "📍 **後半** (3/4 13:00 〜 3/23 15:59):\n"
        "• アリア (5★) - 「殻の中の魂」\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 *情報は公式ソースに基づくものです。ゲーム内でもご確認ください！*"
    )


def main() -> None:
    """Start the bot."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        print("❌ Error: Set TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)
    
    logger.info("Starting Twitter Media Extractor Bot...")
    
    # Build application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("banners", banners_command))
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, debug_message_handler)
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_twitter_url)
    )
    
    logger.info("Bot is running!")
    print("✅ Bot running! Send Twitter URLs to extract media! 🎨")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
