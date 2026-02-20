# 🚀 Quick Start Guide

## Option 1: Automated Setup (Recommended)

```bash
cd /home/openclaw/.nanobot/workspace/projects/twitter-capture
./setup.sh
```

This will:
- ✅ Check Zig installation
- ✅ Install system dependencies
- ✅ Install Python dependencies
- ✅ Build the project
- ✅ Verify everything works

---

## Option 2: Manual Setup

### 1. Install Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install libwebkit2gtk-4.1-dev libgtk-3-dev python3-pip

# Install Python library
pip3 install --user python-telegram-bot
```

### 2. Build the Project

```bash
cd /home/openclaw/.nanobot/workspace/projects/twitter-capture
zig build -Doptimize=ReleaseFast
```

### 3. Test the Binary

```bash
./zig-out/bin/twitter-capture
# Should show usage information
```

---

## 🤖 Setup Telegram Bot

### 1. Create Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow the prompts
4. **Save the token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Configure Bot

Edit `telegram_bot.py`:

```python
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Your token here
```

Or set environment variable:

```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 3. Run the Bot

```bash
cd /home/openclaw/.nanobot/workspace/projects/twitter-capture
python3 telegram_bot.py
```

You should see:
```
🤖 Twitter Capture Bot is running...
Binary: /path/to/twitter-capture
```

---

## 📱 Using the Bot

### In Telegram:

1. **Start the bot**: `/start`
2. **Send a Twitter URL**: 
   ```
   https://twitter.com/username/status/1234567890
   ```
3. **Or use command**: 
   ```
   /tweet https://twitter.com/username/status/1234567890
   ```

The bot will:
- 📸 Capture the tweet as an image
- 🖼️ Send it back to you
- ♻️ Clean up temporary files

---

## 🔧 Running as System Service

### 1. Edit Service File

```bash
cd /home/openclaw/.nanobot/workspace/projects/twitter-capture
nano twitter-bot.service
```

Update the token:
```ini
Environment="TELEGRAM_BOT_TOKEN=your_actual_token_here"
```

### 2. Install Service

```bash
# Copy to systemd directory
sudo cp twitter-bot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable twitter-bot.service
sudo systemctl start twitter-bot.service

# Check status
sudo systemctl status twitter-bot.service
```

### 3. View Logs

```bash
# Real-time logs
sudo journalctl -u twitter-bot.service -f

# Last 50 lines
sudo journalctl -u twitter-bot.service -n 50
```

---

## 🧪 Testing

### Test the Capture Tool

```bash
# Basic test
./zig-out/bin/twitter-capture \
  "https://twitter.com/elonmusk/status/1234567890" \
  test_output.png

# Check if file was created
ls -lh test_output.png
```

### Test the Bot Locally

```bash
# Run in foreground
python3 telegram_bot.py

# Then send a message to your bot in Telegram
```

---

## ⚠️ Troubleshooting

### "Binary not found"

```bash
# Rebuild
cd /home/openclaw/.nanobot/workspace/projects/twitter-capture
zig build -Doptimize=ReleaseFast
```

### "Missing dependencies"

```bash
# Ubuntu/Debian
sudo apt install libwebkit2gtk-4.1-dev libgtk-3-dev

# Arch Linux
sudo pacman -S webkit2gtk-4.1 gtk3
```

### "Bot doesn't respond"

1. Check if bot is running: `ps aux | grep telegram_bot`
2. Check logs: `journalctl -u twitter-bot.service`
3. Verify token is correct
4. Make sure bot is not blocked

### "Capture fails"

- Ensure Twitter URL is public (not protected)
- Check internet connection
- Try a different tweet
- Check system logs for errors

---

## 📊 Project Structure

```
twitter-capture/
├── src/
│   └── main.zig              # Zig source code
├── build.zig                 # Build configuration
├── telegram_bot.py           # Telegram bot (Python)
├── twitter-bot.service       # Systemd service file
├── setup.sh                  # Setup script
├── README.md                 # Full documentation
├── QUICKSTART.md             # This file
└── zig-out/
    └── bin/
        └── twitter-capture   # Compiled binary
```

---

## 🎯 Next Steps

1. ✅ Test with a real Twitter URL
2. ✅ Share the bot with friends
3. 🚀 Deploy to a server for 24/7 operation
4. 🎨 Customize the image output
5. 📈 Add analytics/logging

---

## 📞 Support

- Check `README.md` for detailed documentation
- Review logs: `journalctl -u twitter-bot.service -f`
- Test binary directly for debugging

---

**Happy Capturing! 🐦📸**
