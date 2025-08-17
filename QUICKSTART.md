# 🚀 Quick Start Guide

Get your Officeworks Price Tracker bot running in 5 minutes!

## ⚡ Super Quick Setup

### 1. Install Python
- Download Python 3.8+ from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

### 2. Download & Setup
```bash
# Clone or download this project
cd ow-stock-checker

# Install dependencies
pip install -r requirements.txt
```

### 3. Create Discord Bot
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" → Name it "Officeworks Tracker"
3. Go to "Bot" section → Click "Add Bot"
4. Copy the bot token
5. Go to "OAuth2" → "URL Generator"
6. Select: `bot`, `Send Messages`, `Use Slash Commands`
7. Use the generated URL to invite bot to your server

### 4. Configure Bot
```bash
# Copy environment file
copy env.example .env

# Edit .env and add your bot token
DISCORD_BOT_TOKEN=your_token_here
USE_EPHEMERAL_MESSAGES=true
```

**Note**: Set `USE_EPHEMERAL_MESSAGES=false` if you want bot messages visible to everyone in the channel

### 5. Run Bot
```bash
# Windows
run.bat

# Or manually
python bot.py
```

## 🧪 Test Everything Works

Before running the bot, test the components:

```bash
# Test API connection
python test_api.py

# Test database
python test_database.py
```

## 🎯 First Commands

Once the bot is running:

1. **Setup**: `/setup VIC` (replace VIC with your state)
2. **Add Product**: `/add url:https://www.officeworks.com.au/shop/officeworks/p/ipad-mini-a17-pro-8-3-wifi-128gb-space-grey-ipdmw128g`
3. **Check Status**: `/status`

## ❓ Need Help?

- Check the full [README.md](README.md) for detailed instructions
- Run the test scripts to identify issues
- Make sure your Discord bot has the right permissions

## 🎉 You're Done!

The bot will now:
- Check prices every 30 minutes
- Send you DM notifications when prices drop
- Track your favorite products automatically

Happy shopping! 🛒💰
