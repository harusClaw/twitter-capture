#!/bin/bash
# Quick start script for Twitter Capture Bot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🐦 Twitter URL to Image Converter - Setup"
echo "=========================================="
echo

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ uv found"

# Install dependencies if not already installed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv sync
fi

echo "✅ Dependencies installed"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers (this may take a few minutes)..."
uv run playwright install chromium || {
    echo "⚠️  Browser installation failed. Trying to install system dependencies..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2
        uv run playwright install chromium
    else
        echo "❌ Cannot install system dependencies automatically. Please install manually."
        exit 1
    fi
}

echo "✅ Playwright browsers installed"

# Check for bot token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    if [ -f ".env" ]; then
        echo "📝 Loading token from .env file..."
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo
        echo "⚠️  TELEGRAM_BOT_TOKEN not set!"
        echo
        echo "To get your bot token:"
        echo "1. Open Telegram and search for @BotFather"
        echo "2. Send /newbot command"
        echo "3. Follow the instructions"
        echo "4. Copy the token"
        echo
        echo "Then run:"
        echo "  export TELEGRAM_BOT_TOKEN='your_token_here'"
        echo "  ./quickstart.sh"
        echo
        echo "Or create a .env file:"
        echo "  echo 'TELEGRAM_BOT_TOKEN=your_token_here' > .env"
        echo
        exit 1
    fi
fi

echo "✅ Bot token configured"

echo
echo "🚀 Starting bot..."
echo "=================="
echo
echo "Send Twitter URLs to your bot to get images!"
echo "Commands: /start, /help, /ping"
echo
echo "Press Ctrl+C to stop"
echo

uv run python src/bot.py
