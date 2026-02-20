# Contributing to Twitter Media Extractor

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/harus_claw/twitter-capture.git
cd twitter-capture
```

### 2. Set Up Development Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install Playwright browser
uv run playwright install chromium
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Telegram bot token
```

## 📝 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Keep changes focused and atomic
- Follow existing code style
- Add comments for complex logic

### 3. Test Your Changes

```bash
# Run the bot in development mode
uv run python src/bot.py

# Or run specific test scripts
uv run python dev/test_*.py
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub.

## 🧪 Testing

### Manual Testing

Test with various tweet types:
- Single image tweets
- Multiple image tweets (albums)
- Video tweets
- GIF tweets
- Text-only tweets
- Tweets with links

### Edge Cases

- Private accounts (should fail gracefully)
- Deleted tweets
- NSFW content (handle appropriately)
- Very long tweets
- Tweets with many media files

## 📖 Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Keep functions small and focused
- Add docstrings to public functions
- Use meaningful variable names

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description** - What happened?
2. **Expected Behavior** - What should have happened?
3. **Steps to Reproduce** - How can we reproduce it?
4. **Environment** - Python version, OS, etc.
5. **Logs** - Any error messages

## 💡 Feature Requests

Feature requests are welcome! Please include:

1. **Problem** - What problem does this solve?
2. **Solution** - How should it work?
3. **Alternatives** - Any alternative solutions considered?
4. **Context** - Any additional context or screenshots

## 📄 Pull Request Guidelines

- Keep PRs focused on a single feature/fix
- Update documentation if needed
- Add tests if applicable
- Ensure all existing tests pass
- Be responsive to code review feedback

## 🎯 Areas for Contribution

### High Priority
- Better error handling
- Performance optimizations
- Support for more media types
- Improved media quality extraction

### Medium Priority
- Unit tests
- Integration tests
- CI/CD pipeline
- Docker support

### Nice to Have
- Web interface
- API endpoint
- Multiple bot instances
- Analytics/metrics

## 📞 Getting Help

- Open an issue on GitHub
- Check existing issues and PRs
- Review the codebase
- Ask in the discussions tab

## 🙏 Thank You!

Your contributions make this project better for everyone. Thank you for your time and effort!

---

**Happy coding!** 🚀
