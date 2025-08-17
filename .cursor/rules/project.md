Your goal is to make a simple Discord bot in modern Discord.py that allows users to track the stock and price of a product in Officeworks.

Allow the user to set their closest Officeworks store, add products by parsing the URL for its product code, then follow the example requests and responses to set up a simple scheduled task that can notify the user of price drops.

Use SQLite to store the user's settings and product information, as well as the lowest price, to compare it for price changes.

Use the Discord.py library to create the bot.

Use the requests library to make HTTP requests to the Officeworks API.

Use the datetime library to schedule the task.

Use the sqlite3 library to store the user's settings and product information.

For parsing the URL, take the last part of the URL after the last -, and use that as the product code.

For example, for the URL https://www.officeworks.com.au/shop/officeworks/p/ipad-mini-a17-pro-8-3-wifi-128gb-space-grey-ipdmw128g, the product code is ipdmw128g.

Handle as many edge cases if possible and use slash commands and message components to make the bot simple to use and configure.
