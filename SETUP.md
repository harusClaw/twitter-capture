# 🚀 Quick Setup Guide

## Step 1: Install Playwright Browsers

This is a one-time setup that takes 2-5 minutes:

```bash
cd /home/openclaw/.nanobot/workspace/projects/twitter-capture

# Install Chromium browser
export PATH="$HOME/.local/bin:$PATH"
uv run playwright install chromium
```

**If you get errors about missing system dependencies:**

```bash
# Ubuntu/Debian
sudo uv run playwright install-deps chromium

# Or manually:
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2
```

## Step 2: Get Your Bot Token

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Choose a name and username for your bot
5. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 3: Configure Token

**Option A: Environment Variable**
```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**Option B: Create .env file**
```bash
cp .env.example .env
nano .env  # Edit and add your token
```

## Step 4: Run the Bot

```bash
# Using the quickstart script
./quickstart.sh

# Or manually
uv run python src/bot.py
```

## Step 5: Test in Telegram

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Send a Twitter URL like: `https://twitter.com/elonmusk/status/123456789`

## Troubleshooting

### "Browser doesn't exist" error
```bash
uv run playwright install chromium
```

### "Permission denied" error
```bash
chmod +x quickstart.sh
```

### Bot doesn't respond
- Check if token is correct
- Verify bot is running (check terminal output)
- Make sure bot is not blocked

### Screenshot is blank
- The tweet might be private
- Network issues - try again
- Check bot logs for errors

## Next Steps

- [ ] Set up as systemd service for auto-start
- [ ] Add custom features
- [ ] Deploy to a server

---

**Need help?** Check the full README.md or the troubleshooting section.
