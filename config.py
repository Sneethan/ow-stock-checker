import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

# Firecrawl Configuration
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
# Note: Firecrawl API key is optional - price comparison will work with mock data if not provided

# Message Configuration
USE_EPHEMERAL_MESSAGES = os.getenv('USE_EPHEMERAL_MESSAGES', 'true').lower() == 'true'

def get_discord_timestamp(timestamp, style='R'):
    """Convert a timestamp to Discord's timestamp format
    
    Styles:
    - 't': Short Time (16:20)
    - 'T': Long Time (16:20:30)
    - 'd': Short Date (20/04/2023)
    - 'D': Long Date (20 April 2023)
    - 'f': Short Date/Time (20 April 2023 16:20)
    - 'F': Long Date/Time (Thursday, 20 April 2023 16:20)
    - 'R': Relative Time (2 months ago, in 3 days)
    """
    if not timestamp:
        return "Never"
    
    # Ensure timestamp is a datetime object
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return "Unknown"
    
    # Ensure timestamp has timezone info
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    # Convert to UNIX timestamp (seconds since epoch)
    unix_timestamp = int(timestamp.timestamp())
    
    # Return Discord timestamp format
    return f"<t:{unix_timestamp}:{style}>"

def get_relative_timestamp(timestamp):
    """Convert a timestamp to Discord's relative timestamp format (e.g., '2 hours ago')"""
    return get_discord_timestamp(timestamp, 'R')

def get_future_relative_time(timestamp):
    """Convert a future timestamp to Discord's relative timestamp format (e.g., 'In 2 hours')"""
    return get_discord_timestamp(timestamp, 'R')

def get_full_timestamp(timestamp):
    """Convert a timestamp to Discord's full date/time format"""
    return get_discord_timestamp(timestamp, 'F')

def get_short_timestamp(timestamp):
    """Convert a timestamp to Discord's short date/time format"""
    return get_discord_timestamp(timestamp, 'f')

# Officeworks API Configuration
OFFICEWORKS_API_BASE = "https://api.youinstock.com/officeworks/api"
OFFICEWORKS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Priority": "u=0"
}

# Database Configuration
DATABASE_PATH = "officeworks_bot.db"

# Price Check Interval (in minutes)
PRICE_CHECK_INTERVAL = 30

# Australian States and Territories for store selection
AUSTRALIAN_STATES = [
    "ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"
]

# State names for display
STATE_NAMES = {
    "ACT": "Australian Capital Territory",
    "NSW": "New South Wales", 
    "NT": "Northern Territory",
    "QLD": "Queensland",
    "SA": "South Australia",
    "TAS": "Tasmania",
    "VIC": "Victoria",
    "WA": "Western Australia"
}
