# Officeworks Price Tracker Discord Bot

A Discord bot that allows users to track Officeworks product prices and get notified of price drops automatically.

## Features

- 🏪 **Store Setup**: Set your preferred Officeworks store location
- 📦 **Product Tracking**: Add products by URL or product code
- 💰 **Price Monitoring**: Automatic price checking every 30 minutes
- 🔔 **Notifications**: Get DM notifications when prices drop
- 📊 **Price History**: Track lowest prices and price changes
- 🛠️ **Easy Commands**: Simple slash commands for all operations

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- A Discord account
- A Discord bot token

### 2. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the bot token (you'll need this later)
6. Go to "OAuth2" > "URL Generator"
7. Select "bot" scope and the following permissions:
   - Send Messages
   - Use Slash Commands
   - Send Messages in Threads
   - Use External Emojis
   - Add Reactions
8. Use the generated URL to invite the bot to your server

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Setup

1. Copy `env.example` to `.env`
2. Edit `.env` and add your Discord bot token:
   ```
   DISCORD_BOT_TOKEN=your_actual_bot_token_here
   USE_EPHEMERAL_MESSAGES=true
   ```

   **Note**: Set `USE_EPHEMERAL_MESSAGES=false` to make bot messages visible to everyone in the channel (default: `true` for private messages)

### 5. Run the Bot

```bash
python bot.py
```

## Usage

### Getting Started

1. **Setup Store**: Use `/setup` to set your preferred Officeworks store location
2. **Add Products**: Use `/add` with an Officeworks product URL to start tracking
3. **Monitor**: The bot automatically checks prices every 30 minutes
4. **Get Notified**: Receive DM notifications when prices drop

### Commands

#### Setup Commands
- `/setup` - Set your preferred store location
- `/stores` - List available stores in a state

#### Product Commands
- `/add` - Add a product to track (by URL or product code)
- `/list` - List your tracked products
- `/check` - Manually check a product price
- `/remove` - Remove a product from tracking

#### Utility Commands
- `/status` - Check bot and monitoring status
- `/help` - Show help information

### Example Usage

```
/add url:https://www.officeworks.com.au/shop/officeworks/p/ipad-mini-a17-pro-8-3-wifi-128gb-space-grey-ipdmw128g
```

This will extract the product code `ipdmw128g` and start tracking the iPad Mini.

## How It Works

1. **URL Parsing**: The bot extracts product codes from Officeworks URLs (last part after the final dash)
2. **API Integration**: Uses the Officeworks stock-check API to get real-time pricing
3. **Database Storage**: SQLite database stores user preferences and product information
4. **Scheduled Monitoring**: APScheduler runs price checks every 30 minutes
5. **Smart Notifications**: Only sends notifications when prices actually drop

## File Structure

```
ow-stock-checker/
├── bot.py              # Main Discord bot file
├── config.py           # Configuration and constants
├── database.py         # SQLite database operations
├── officeworks_api.py  # Officeworks API client
├── price_checker.py    # Price monitoring and notifications
├── requirements.txt    # Python dependencies
├── env.example        # Environment variables template
└── README.md          # This file
```

## Configuration

The bot can be configured by editing `config.py` or setting environment variables:

### Environment Variables
- **DISCORD_BOT_TOKEN**: Your Discord bot token (required)
- **USE_EPHEMERAL_MESSAGES**: Control whether bot messages are private (`true`) or public (`false`)

### Config File Options
- **Price Check Interval**: Change how often prices are checked (default: 30 minutes)
- **API Headers**: Modify request headers if needed
- **Database Path**: Change SQLite database location

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check if the bot token is correct and the bot is online
2. **Commands not working**: Ensure the bot has the required permissions in your server
3. **API errors**: The Officeworks API might be temporarily unavailable
4. **Database errors**: Check file permissions for the SQLite database

### Logs

The bot provides console output for debugging:
- Bot startup and connection status
- Price check operations
- API request results
- Error messages

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

