# Twitter Media Extractor 🐦📸

A Telegram bot that extracts and sends images, videos, and GIFs from Twitter/X URLs.

## ✨ Features

- 🖼️ **Extract Images** - Get all images from tweets (up to 4)
- 🎬 **Extract Videos** - Download and send native videos
- 🎨 **GIF Support** - Animated GIFs sent as playable videos
- 📱 **Native Telegram Messages** - Media sent as photos/videos, not documents
- 🎯 **Album Support** - Multiple images sent as swipeable albums
- 📝 **Tweet Text** - Includes tweet content, username, and timestamp
- 🔒 **No Login Required** - Uses fixupx.com to bypass Twitter walls
- ⚡ **Fast & Lightweight** - Built with Playwright and python-telegram-bot

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Playwright browser
uv run playwright install chromium

# Install system dependencies (if needed)
uv run playwright install-deps chromium
```

### 2. Get Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token

### 3. Configure Environment

Create a `.env` file:

```bash
echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env
```

Or export as environment variable:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

### 4. Run the Bot

```bash
uv run python src/bot.py
```

### 5. Use in Telegram

- Start a chat with your bot
- Send any Twitter/X URL
- Receive all media from the tweet!

**Example URLs:**
- `https://twitter.com/username/status/123456`
- `https://x.com/username/status/123456`

## 📖 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show welcome message |
| `/help` | Show help and usage instructions |
| `/ping` | Check if bot is alive |

## 🏗️ Project Structure

```
twitter-capture/
├── src/
│   ├── bot.py              # Main bot application
│   └── media_extractor.py  # Alternative simpler bot
├── dev/                    # Development and debug scripts
├── .env                    # Environment variables (gitignored)
├── .env.example            # Example environment file
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lock file
├── telegram_bot.service    # Systemd service template
├── quickstart.sh           # Quick setup script
├── LICENSE                 # MIT License
└── README.md               # This file
```

## 🔧 Systemd Service (Optional)

Run the bot as a background service:

### 1. Create Service File

```bash
cp telegram_bot.service ~/.config/systemd/user/
```

### 2. Edit Configuration

Edit the service file and set your bot token:

```bash
nano ~/.config/systemd/user/telegram_bot.service
```

### 3. Enable and Start

```bash
systemctl --user daemon-reload
systemctl --user enable telegram_bot.service
systemctl --user start telegram_bot.service

# Check status
systemctl --user status telegram_bot.service

# View logs
journalctl --user -u telegram_bot.service -f
```

## 🛠️ Development

### Debug Scripts

The `dev/` folder contains various debug and test scripts:

- `debug_*.py` - Media extraction debugging
- `test_*.py` - Feature testing scripts

### Run in Development Mode

```bash
# Enable debug logging
export PYTHONDEBUG=1
uv run python src/bot.py
```

### Add New Features

The main bot logic is in `src/bot.py`. Key functions:

- `extract_tweet_data()` - Extracts tweet content using Playwright
- `handle_twitter_url()` - Processes incoming Twitter URLs
- `download_file()` - Downloads media files

## 📋 Requirements

- Python 3.10+
- uv (Python package manager)
- Playwright (Chromium browser)
- Telegram Bot Token
- Internet connection

## 🔒 Security Notes

- ⚠️ **Never commit your bot token** to version control
- ✅ Use environment variables or `.env` files
- ✅ The `.env` file is gitignored by default
- ✅ Run with minimal privileges

## 🐛 Troubleshooting

### Browser Installation Fails

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 libcairo2

# Reinstall browsers
uv run playwright install chromium
```

### Bot Doesn't Respond

1. Check if bot is running: `ps aux | grep bot.py`
2. Check logs: `journalctl --user -u telegram_bot.service -f`
3. Verify token is correct
4. Ensure the Twitter account is public (not private)

### "No media found" Error

- Tweet might be from a private account
- Tweet might have been deleted
- Network issues - try again
- Some tweets only have text (no media)

### Timeout Errors

- Increase timeout in `extract_tweet_data()`
- Check network connectivity
- Twitter API might be rate-limited

## 📝 How It Works

1. User sends a Twitter/X URL to the bot
2. Bot navigates to fixupx.com (Twitter embed service)
3. Playwright extracts media URLs from the page
4. Bot downloads images/videos
5. Media sent to user as native Telegram messages

## 🌟 Examples

### Single Image Tweet
```
Input: https://x.com/artist/status/123456
Output: 📷 Image sent as photo + tweet text
```

### Multiple Images (Album)
```
Input: https://x.com/photographer/status/789012
Output: 📸 4 images sent as swipeable album
```

### Video Tweet
```
Input: https://x.com/creator/status/345678
Output: 🎬 Video sent as native Telegram video
```

### GIF Tweet
```
Input: https://x.com/animator/status/901234
Output: 🎨 GIF sent as playable video
```

## 📄 License

MIT License - Feel free to modify and distribute!

## 🙏 Acknowledgments

- [fixupx.com](https://fixupx.com) - Twitter embed service
- [Playwright](https://playwright.dev) - Browser automation
- [python-telegram-bot](https://python-telegram-bot.org) - Telegram Bot API

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Playwright documentation
3. Check Telegram Bot API docs

---

**Enjoy extracting Twitter media!** 🐦🎨
