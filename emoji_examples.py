#!/usr/bin/env python3
"""
Examples of how to use custom emojis in your Officeworks bot
"""

from emojis import *
from colors import *

def example_embed_with_custom_emojis():
    """Example of creating an embed with custom emojis"""
    
    # Create embed with custom emojis
    embed = discord.Embed(
        title=f"{STORE} Officeworks Store Setup",
        description=f"{SUCCESS} Your store preferences have been configured!",
        color=SUCCESS_COLOR,
        timestamp=datetime.now()
    )
    
    # Add fields with emojis
    embed.add_field(
        name=f"{LOCATION} Store Location",
        value="Melbourne CBD",
        inline=True
    )
    
    embed.add_field(
        name=f"{PHONE} Contact",
        value="(03) 9691 4500",
        inline=True
    )
    
    embed.add_field(
        name=f"{STORE_ID} Store ID",
        value="W346",
        inline=True
    )
    
    embed.add_field(
        name=f"{ADDRESS} Full Address",
        value="Shop 1 & 2 461 Bourke Street, Melbourne VIC 3000",
        inline=False
    )
    
    embed.set_footer(text=f"{INFO} Use /add to start tracking products")
    
    return embed

def example_button_with_custom_emojis():
    """Example of creating buttons with custom emojis"""
    
    # Create a button with custom emoji
    search_button = discord.ui.Button(
        label=f"{SEARCH} Search Stores",
        style=discord.ButtonStyle.primary,
        emoji=SEARCH
    )
    
    browse_button = discord.ui.Button(
        label=f"{BROWSE} Browse All",
        style=discord.ButtonStyle.secondary,
        emoji=BROWSE
    )
    
    back_button = discord.ui.Button(
        label=f"{BACK_ARROW} Back",
        style=discord.ButtonStyle.danger,
        emoji=BACK_ARROW
    )
    
    return [search_button, browse_button, back_button]

def example_status_message():
    """Example of creating status messages with emojis"""
    
    # Bot status
    bot_status = f"{BOT} Bot Status: Online"
    
    # Store status
    store_status = f"{STORE} Store: Melbourne CBD"
    
    # Product status
    product_status = f"{PRODUCT} Tracking: 5 products"
    
    # Price monitoring
    monitoring_status = f"{PROCESSING} Price monitoring: Active"
    
    return f"{bot_status}\n{store_status}\n{product_status}\n{monitoring_status}"

def example_product_embed(product_name, price, stock_level):
    """Example of creating a product embed with dynamic emojis"""
    
    # Determine stock emoji based on level
    if stock_level > 10:
        stock_emoji = AVAILABILITY
        stock_text = "In Stock"
        color = SUCCESS_COLOR
    elif stock_level > 0:
        stock_emoji = WARNING
        stock_text = "Low Stock"
        color = WARNING_COLOR
    else:
        stock_emoji = UNAVAILABLE
        stock_text = "Out of Stock"
        color = ERROR_COLOR
    
    # Create embed
    embed = discord.Embed(
        title=f"{PRODUCT} {product_name}",
        description=f"{PRICE} Current Price: ${price:.2f}",
        color=color,
        timestamp=datetime.now()
    )
    
    # Add stock information
    embed.add_field(
        name=f"{stock_emoji} Stock Status",
        value=stock_text,
        inline=True
    )
    
    embed.add_field(
        name=f"{TIME} Last Updated",
        value="Just now",
        inline=True
    )
    
    embed.add_field(
        name=f"{INFO} Product Code",
        value="ABC123",
        inline=True
    )
    
    return embed

def example_custom_discord_emojis():
    """Example of how to use custom Discord emojis"""
    
    # When you add custom Discord emojis to emojis.py:
    # OFFICEWORKS_LOGO = "<:ow_logo:123456789>"
    # OFFICEWORKS_STORE = "<:ow_store:987654321>"
    
    # You can use them like this:
    # embed.title = f"{OFFICEWORKS_LOGO} Officeworks Bot"
    # embed.add_field(name=f"{OFFICEWORKS_STORE} Store Info", value=store_info)
    
    # For now, we'll use the standard emojis
    embed = discord.Embed(
        title=f"{STORE} Officeworks Store",
        description=f"{SUCCESS} Store information loaded successfully!",
        color=PRIMARY_COLOR
    )
    
    return embed

def example_emoji_groups():
    """Example of using emoji groups for consistency"""
    
    # Use the predefined emoji groups
    embed = discord.Embed(
        title=f"{STORE_EMOJIS['store']} Store Information",
        color=INFO_COLOR
    )
    
    # Add fields using grouped emojis
    embed.add_field(
        name=f"{STORE_EMOJIS['location']} Location",
        value="Melbourne CBD",
        inline=True
    )
    
    embed.add_field(
        name=f"{STORE_EMOJIS['phone']} Phone",
        value="(03) 9691 4500",
        inline=True
    )
    
    embed.add_field(
        name=f"{STORE_EMOJIS['id']} Store ID",
        value="W346",
        inline=True
    )
    
    return embed

def example_conditional_emojis(bot_status, store_count, product_count):
    """Example of using conditional emojis based on status"""
    
    # Bot status emoji
    bot_emoji = ONLINE if bot_status == "online" else OFFLINE
    
    # Store count emoji
    if store_count > 50:
        store_emoji = STATISTICS
    elif store_count > 10:
        store_emoji = STORE
    else:
        store_emoji = WARNING
    
    # Product count emoji
    if product_count > 100:
        product_emoji = PRODUCT
    elif product_count > 10:
        product_emoji = PRICE
    else:
        product_emoji = QUESTION
    
    # Create status message
    status_message = f"""
{bot_emoji} **Bot Status**: {bot_status.title()}
{store_emoji} **Stores Available**: {store_count}
{product_emoji} **Products Tracked**: {product_count}
    """.strip()
    
    return status_message

# Example usage in your bot:
"""
# In your bot commands, you can now use:

from emojis import *

# Simple usage
embed.title = f"{SUCCESS} Operation Complete!"

# Button labels
button = discord.ui.Button(label=f"{SEARCH} Search")

# Field names
embed.add_field(name=f"{LOCATION} Address", value=address)

# Status messages
status = f"{ONLINE} Bot is ready!"
"""
