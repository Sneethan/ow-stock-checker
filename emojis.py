# 🎨 Custom Emoji Configuration
# Add your custom emojis here and they'll be used throughout the bot
# You can use Discord custom emojis, Unicode emojis, or text symbols

# =============================================================================
# NAVIGATION & ACTIONS
# =============================================================================
BACK_ARROW = "<:arrowleft32x:1406486282565062667>"           # Back buttons
BACK_ICON = "<:arrowleft32x:1406486282565062667>"            # Back to previous view
SUCCESS = "<:circlecheck32x:1406486309375312073>"              # Success/completion
ERROR = "<:circlexmark32x:1406486340396384406>"                # Errors/failures
PROCESSING = "<:reuse32x:1406486429076557904>"           # Processing/monitoring
LOADING = "<:hourglassend32x:1406486945361694780>"              # Loading states

# =============================================================================
# STORE & LOCATION
# =============================================================================
STORE = "<:shop32x:1406486445878804592>"                # Store/Officeworks
LOCATION = "<:location332x:1406486370976792698>"             # Address/location
PHONE = "<:phone32x:1406486415935803453>"                # Phone number
STORE_ID = "<:numberinput32x:1406486401049952336>"             # Store ID
ADDRESS = "<:location332x:1406486370976792698>"              # Address icon

# =============================================================================
# SEARCH & BROWSE
# =============================================================================
SEARCH = "<:magnifier32x:1406486385380163596>"               # Search functionality
BROWSE = "<:clipboardlist32x:1406486355625771189>"               # Browse/list view
FILTER = "<:filter32x:1406492183552594041>"               # Filter options
SORT = "<:chart32x:1406491893659078748>"                 # Sort options

# =============================================================================
# PRODUCT MANAGEMENT
# =============================================================================
PRODUCT = "<:box232x:1406491683088109618>"              # Products
PRICE = "<:tag332x:1406486457425854554>"                # Price information
PRICE_DROP = "<:arrowtrenddown32x:1406491499524259891>"           # Price drops/savings
TIME = "<:circlehalfdottedclock32x:1406486325607006319>"                 # Time/last checked
STOCK = "<:box232x:1406491683088109618>"                # Stock levels
AVAILABILITY = "<:circlecheck32x:1406486309375312073>"         # Available
UNAVAILABLE = "<:circlexmark32x:1406486340396384406>"          # Not available

# =============================================================================
# STATUS & INFORMATION
# =============================================================================
BOT = "<:circlehalfdottedclock32x:1406486325607006319>"                  # Bot status
STATISTICS = "📊"           # Statistics/data
HELP = "📚"                 # Help/documentation
TOOLS = "🛠️"               # Utility tools
GETTING_STARTED = "🚀"      # Getting started
SETTINGS = "⚙️"             # Settings/configuration

# =============================================================================
# COLORS & INDICATORS
# =============================================================================
ONLINE = "<:signal232x:1406494965764329552>"               # Online/active status
OFFLINE = "<:signal2off32x:1406495106571309077>"              # Offline/inactive status
WARNING = "⚠️"              # Warnings
TIP = "💡"                  # Examples/tips
INFO = "ℹ️"                 # Information
QUESTION = "❓"              # Questions

# =============================================================================
# NOTIFICATIONS & ALERTS
# =============================================================================
NOTIFICATION = "🔔"         # General notifications
ALERT = "🚨"                # Important alerts
BELL = "🔔"                 # Notification bell
STAR = "⭐"                 # Favorites/important

# =============================================================================
# SHOPPING & COMMERCE
# =============================================================================
CART = "🛒"                 # Shopping cart
TAG = "🏷️"                 # Price tags
SALE = "🏷️"                # Sale items
DISCOUNT = "💸"             # Discounts/savings
GIFT = "🎁"                 # Special offers
COMPARE = "⚖️"              # Price comparison
PRICE_MATCH = "🎯"          # Price match opportunities
EXTERNAL_LINK = "🔗"        # External retailer links

# =============================================================================
# TIME & SCHEDULING
# =============================================================================
CALENDAR = "📅"             # Calendar/scheduling
CLOCK = "🕐"                # Time
TIMER = "⏰"                # Timers/deadlines
HISTORY = "📜"              # History/past

# =============================================================================
# USER & PROFILE
# =============================================================================
USER = "👤"                 # User profile
SETTINGS_USER = "⚙️"        # User settings
PROFILE = "👤"              # User profile
PREFERENCES = "❤️"          # User preferences

# =============================================================================
# OFFICEWORKS SPECIFIC
# =============================================================================
# You can add Officeworks-specific emojis here
# For example, if you have custom Discord emojis:
# OFFICEWORKS_LOGO = "<:ow_logo:123456789>"  # Custom Discord emoji
# OFFICEWORKS_STORE = "<:ow_store:123456789>" # Custom Discord emoji

# =============================================================================
# CUSTOM DISCORD EMOJI EXAMPLES
# =============================================================================
# To add your own custom emojis:
# 1. Upload emoji to your Discord server
# 2. Right-click and copy emoji ID
# 3. Uncomment and replace the examples below

# Officeworks Brand Emojis
# OFFICEWORKS_LOGO = "<:ow_logo:123456789>"
# OFFICEWORKS_STORE = "<:ow_store:123456789>"
# OFFICEWORKS_BAG = "<:ow_bag:123456789>"
# OFFICEWORKS_CART = "<:ow_cart:123456789>"

# Product Category Emojis
# ELECTRONICS = "<:electronics:123456789>"
# STATIONERY = "<:stationery:123456789>"
# FURNITURE = "<:furniture:123456789>"
# OFFICE_SUPPLIES = "<:office_supplies:123456789>"

# Status Emojis
# IN_STOCK = "<:in_stock:123456789>"
# LOW_STOCK = "<:low_stock:123456789>"
# OUT_OF_STOCK = "<:out_of_stock:123456789>"
# ON_SALE = "<:on_sale:123456789>"

# =============================================================================
# EMOJI GROUPS (for easy access)
# =============================================================================

# Navigation group
NAVIGATION_EMOJIS = {
    "back": BACK_ARROW,
    "back_icon": BACK_ICON,
    "success": SUCCESS,
    "error": ERROR,
    "processing": PROCESSING,
    "loading": LOADING
}

# Store group
STORE_EMOJIS = {
    "store": STORE,
    "location": LOCATION,
    "phone": PHONE,
    "id": STORE_ID,
    "address": ADDRESS
}

# Product group
PRODUCT_EMOJIS = {
    "product": PRODUCT,
    "price": PRICE,
    "price_drop": PRICE_DROP,
    "time": TIME,
    "stock": STOCK,
    "available": AVAILABILITY,
    "unavailable": UNAVAILABLE
}

# Status group
STATUS_EMOJIS = {
    "online": ONLINE,
    "offline": OFFLINE,
    "warning": WARNING,
    "info": INFO,
    "question": QUESTION
}

# =============================================================================
# USAGE EXAMPLES
# =============================================================================
"""
# How to use these emojis in your bot:

from emojis import *

# Single emoji
embed.title = f"{SUCCESS} Setup Complete!"

# Multiple emojis
message = f"{STORE} Store: {STORE_NAME}\n{PRICE} Price: ${PRICE_VALUE}"

# In button labels
button = discord.ui.Button(label=f"{SEARCH} Search Stores")

# In embed fields
embed.add_field(name=f"{LOCATION} Address", value=address)
embed.add_field(name=f"{PHONE} Phone", value=phone)

# With custom Discord emojis (when you add them):
# embed.title = f"{OFFICEWORKS_LOGO} Officeworks Bot"
"""

# =============================================================================
# CUSTOMIZATION NOTES
# =============================================================================
"""
# To add custom Discord emojis:
1. Upload your emoji to your Discord server
2. Right-click the emoji and copy its ID
3. Use the format: CUSTOM_EMOJI = "<:emoji_name:emoji_id>"
4. Example: OFFICEWORKS_LOGO = "<:ow_logo:123456789>"

# To use Unicode emojis:
# Just replace the value with your preferred emoji
# Example: STORE = "🏢"  # Corporate building instead of store

# To use text symbols:
# You can use ASCII art or text symbols
# Example: SUCCESS = "✓"  # Checkmark instead of green checkmark

# To disable emojis:
# Set the value to an empty string
# Example: STORE = ""  # No emoji, just text
"""
