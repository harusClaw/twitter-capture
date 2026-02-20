#!/bin/bash
# Quick setup script for Twitter Media Extractor

set -e

echo "🚀 Setting up Twitter Media Extractor..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
uv sync

# Install Playwright browser
echo "🌐 Installing Playwright browser..."
uv run playwright install chromium

# Optional: Install system dependencies
echo "🔧 Checking system dependencies..."
if command -v apt-get &> /dev/null; then
    echo "   Installing system dependencies (may require sudo)..."
    sudo apt-get update || true
    sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 \
        libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
        libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
        libgbm1 libasound2 libpango-1.0-0 libcairo2 || true
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "   ⚠️  Please edit .env and add your Telegram bot token!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Edit .env and add your TELEGRAM_BOT_TOKEN"
echo "   2. Run the bot: uv run python src/bot.py"
echo "   3. Send Twitter URLs to your bot on Telegram!"
echo ""
echo "🎉 Happy tweeting!"
