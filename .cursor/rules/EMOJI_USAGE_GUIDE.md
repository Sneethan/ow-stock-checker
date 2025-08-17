# 🎨 Custom Emoji Usage Guide

## 🚀 **Quick Start**

### **1. Import Emojis**
```python
from emojis import *
```

### **2. Use in Your Code**
```python
# In embed titles
embed.title = f"{SUCCESS} Setup Complete!"

# In button labels
button = discord.ui.Button(label=f"{SEARCH} Search Stores")

# In embed fields
embed.add_field(name=f"{LOCATION} Address", value=address)
```

## 📱 **Available Emoji Categories**

### **Navigation & Actions**
- `BACK_ARROW` - ⬅️
- `BACK_ICON` - 🔙
- `SUCCESS` - ✅
- `ERROR` - ❌
- `PROCESSING` - 🔄
- `LOADING` - ⏳

### **Store & Location**
- `STORE` - 🏪
- `LOCATION` - 📍
- `PHONE` - 📞
- `STORE_ID` - 🆔
- `ADDRESS` - 🏠

### **Search & Browse**
- `SEARCH` - 🔍
- `BROWSE` - 📋
- `FILTER` - 🔧
- `SORT` - 📊

### **Product Management**
- `PRODUCT` - 📦
- `PRICE` - 💰
- `PRICE_DROP` - 📉
- `TIME` - 🕒
- `STOCK` - 📦
- `AVAILABILITY` - ✅
- `UNAVAILABLE` - ❌

### **Status & Information**
- `BOT` - 🤖
- `STATISTICS` - 📊
- `HELP` - 📚
- `TOOLS` - 🛠️
- `GETTING_STARTED` - 🚀
- `SETTINGS` - ⚙️

## 🎯 **Adding Custom Discord Emojis**

### **Step 1: Upload to Discord**
1. Go to your Discord server
2. Go to Server Settings → Emojis
3. Upload your custom emoji
4. Note the emoji name

### **Step 2: Get Emoji ID**
1. In Discord, type `\:emoji_name:`
2. Copy the ID that appears
3. Example: `\:ow_logo:` shows `<:ow_logo:123456789>`

### **Step 3: Add to emojis.py**
```python
# In emojis.py
OFFICEWORKS_LOGO = "<:ow_logo:123456789>"
OFFICEWORKS_STORE = "<:ow_store:987654321>"
```

### **Step 4: Use in Your Bot**
```python
from emojis import OFFICEWORKS_LOGO

embed.title = f"{OFFICEWORKS_LOGO} Officeworks Bot"
```

## 🔧 **Customization Examples**

### **Change Store Icon**
```python
# In emojis.py
STORE = "🏢"  # Corporate building instead of store
# or
STORE = "<:officeworks:123456789>"  # Custom Discord emoji
```

### **Change Success Icon**
```python
# In emojis.py
SUCCESS = "✓"  # Simple checkmark
# or
SUCCESS = "<:success_green:123456789>"  # Custom Discord emoji
```

### **Disable Emojis**
```python
# In emojis.py
STORE = ""  # No emoji, just text
```

## 📋 **Common Use Cases**

### **Button Labels**
```python
button = discord.ui.Button(
    label=f"{SEARCH} Search",
    style=discord.ButtonStyle.primary
)
```

### **Embed Titles**
```python
embed = discord.Embed(
    title=f"{SUCCESS} Operation Complete",
    color=SUCCESS_COLOR
)
```

### **Field Names**
```python
embed.add_field(
    name=f"{LOCATION} Store Location",
    value=store_address
)
```

### **Status Messages**
```python
status_message = f"{ONLINE} Bot is online and ready!"
```

## 🎨 **Brand Consistency Tips**

### **Officeworks Branding**
- Use `OFFICEWORKS_LOGO` for main bot identity
- Use `OFFICEWORKS_STORE` for store-related features
- Use `OFFICEWORKS_CART` for shopping features

### **Color Coordination**
- Match emoji colors with your embed colors
- Use consistent emoji styles across similar functions
- Consider accessibility (high contrast)

### **Emoji Groups**
```python
# Use grouped emojis for consistency
from emojis import STORE_EMOJIS

embed.add_field(
    name=f"{STORE_EMOJIS['store']} Store Info",
    value=f"{STORE_EMOJIS['location']} {address}"
)
```

## 🔄 **Updating Existing Code**

### **Before (Hardcoded)**
```python
embed.title = "✅ Setup Complete!"
button = discord.ui.Button(label="🔍 Search")
```

### **After (Customizable)**
```python
embed.title = f"{SUCCESS} Setup Complete!"
button = discord.ui.Button(label=f"{SEARCH} Search")
```

## 📚 **Advanced Usage**

### **Conditional Emojis**
```python
status_emoji = ONLINE if bot.is_ready() else OFFLINE
status_message = f"{status_emoji} Bot Status: {status}"
```

### **Dynamic Emojis**
```python
def get_stock_emoji(stock_level):
    if stock_level > 10:
        return AVAILABILITY
    elif stock_level > 0:
        return WARNING
    else:
        return UNAVAILABLE
```

### **Emoji Arrays**
```python
# Create emoji sequences
loading_sequence = [LOADING, PROCESSING, "⏳", "⌛"]
current_loading = loading_sequence[loading_index % len(loading_sequence)]
```

## 🚨 **Troubleshooting**

### **Emoji Not Showing**
- Check if the emoji exists in your Discord server
- Verify the emoji ID is correct
- Ensure the bot has access to the emoji

### **Custom Emoji Not Working**
- Make sure the emoji is in a server the bot can see
- Check the format: `<:name:id>`
- Verify the bot has permissions to use external emojis

### **Unicode Emoji Issues**
- Test emojis on different platforms
- Consider using custom Discord emojis for consistency
- Ensure emojis are supported across devices
