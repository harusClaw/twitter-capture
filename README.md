# Twitter Capture 🐦📸

A Telegram bot that extracts images, videos, and GIFs from Twitter/X URLs and sends them as native Telegram media.

## ✨ Features

- 🖼️ **Images** - Extract all images from tweets (up to 4)
- 🎬 **Videos** - Download and send native videos
- 🎨 **GIFs** - Animated GIFs sent as playable videos
- 📱 **Native Media** - Sent as photos/videos, not documents
- 🎯 **Albums** - Multiple images as swipeable albums
- 📝 **Tweet Context** - Includes username, text, and timestamp
- 🔒 **No Login** - Uses fixupx.com to bypass Twitter walls
- ⚡ **Fast** - Built with Playwright and python-telegram-bot

## 🚀 Quick Start

### 1. Install Dependencies

```bash
uv sync
uv run playwright install chromium
```

### 2. Configure Bot Token

Create a `.env` file with your Telegram bot token:

```bash
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env
```

Get a token from [@BotFather](https://t.me/BotFather) on Telegram.

### 3. Run the Bot

```bash
uv run python -m twitter_capture
```

### 4. Use in Telegram

Send any Twitter/X URL to your bot:
- `https://twitter.com/user/status/123`
- `https://x.com/user/status/123`

## 📖 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Usage instructions |
| `/ping` | Check bot status |

## 🏗️ Structure

```
twitter-capture/
├── src/twitter_capture/
│   ├── __init__.py      # Package info
│   ├── __main__.py      # Entry point
│   ├── bot.py           # Telegram bot
│   └── extractor.py     # Media extraction
├── .env.example         # Environment template
├── pyproject.toml       # Project config
├── twitter-bot.service  # Systemd template
└── README.md
```

## 🔧 Systemd Service (Optional)

Run as a background service:

```bash
# Copy service file
cp twitter-bot.service ~/.config/systemd/user/

# Edit and set your token, then:
systemctl --user daemon-reload
systemctl --user enable --now twitter-bot.service

# Check status
systemctl --user status twitter-bot.service
```

## 🛠️ Development

### Run in Debug Mode

```bash
export PYTHONDEBUG=1
uv run python -m twitter_capture
```

### Key Files

- `bot.py` - Main bot logic and Telegram handlers
- `extractor.py` - Playwright-based tweet extraction

## 🐛 Troubleshooting

**Browser installation fails:**
```bash
uv run playwright install-deps chromium
```

**Bot doesn't respond:**
- Check logs: `journalctl --user -u twitter-bot -f`
- Verify token is correct
- Ensure Twitter account is public

**"No media found":**
- Tweet may be private or deleted
- Some tweets are text-only

## 🔒 Security

- ⚠️ Never commit `.env` with your bot token
- ✅ Token is gitignored by default
- ✅ Run with minimal privileges

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 🙏 Credits

- [fixupx.com](https://fixupx.com) - Twitter embed service
- [Playwright](https://playwright.dev) - Browser automation
- [python-telegram-bot](https://python-telegram-bot.org) - Bot framework

---

**Made by harus_claw** 🐾
