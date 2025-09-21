# Setting Up Firecrawl for Price Comparison

The price comparison feature is now integrated into your Officeworks Stock Checker bot! Here's how to enable full functionality with real web scraping.

## Current Status

✅ **Implemented Features:**
- Price comparison system with 4 major retailers (JB Hi-Fi, Harvey Norman, The Good Guys, Officeworks)
- Enhanced `/check` command with `compare_prices` parameter
- New standalone `/compare` command for any product search
- Intelligent product matching and price analysis
- Price match opportunity detection
- Beautiful Discord embeds with comparison results
- Rate limiting and error handling
- Mock Firecrawl integration (ready for real API)

⚠️ **Needs Configuration:**
- Firecrawl API for live web scraping

## Quick Setup (Recommended)

The bot is now configured to use the Firecrawl Python SDK! Here's how to enable it:

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```
(This will install `firecrawl-py` along with other dependencies)

### Step 2: Get Firecrawl API Key
1. Visit [Firecrawl.dev](https://firecrawl.dev)
2. Sign up for an account
3. Get your API key from the dashboard

### Step 3: Configure Environment Variable
Add to your `.env` file:
```
FIRECRAWL_API_KEY=your_api_key_here
```

### Step 4: Restart the Bot
The bot will automatically detect the API key and enable real web scraping!

## Current Status

✅ **Ready to Use:**
- Firecrawl Python SDK integration is complete ✅
- **NEW:** Firecrawl Extract feature for structured data extraction 🔥
- Automatic fallback to traditional scraping when needed
- All price comparison features implemented
- Enhanced fuzzy matching for better product detection
- Real-time price extraction from retailer websites

⚠️ **To Enable Live Data:**
- Configure `FIRECRAWL_API_KEY` environment variable
- Restart the bot
- Results will show "🔍 AI Enhanced" for Extract-powered matches

## Testing the Full Implementation

After configuring Firecrawl, test the functionality:

### Test Enhanced Check Command
```
/check product_code:ipdmw128g compare_prices:True
```

### Test Standalone Compare Command
```
/compare search_query:"iPad Mini 128GB"
/compare search_query:"Sony WH-1000XM4" officeworks_price:399.00
```

## Expected Results

With Firecrawl properly configured, you should see:

1. **Real Price Data**: Actual prices from JB Hi-Fi, Harvey Norman, The Good Guys, etc.
2. **Price Match Opportunities**: Clear indicators when competitors have lower prices
3. **Detailed Product Information**: Better product matching and descriptions
4. **Up-to-date Pricing**: Current prices from retailer websites

## Troubleshooting

### Common Issues

1. **"Firecrawl MCP not available"**
   - Install Firecrawl Python SDK
   - Configure API key properly
   - Check internet connection

2. **"No price comparisons found"**
   - Try simpler search terms
   - Check if retailers have the product in stock
   - Verify the product exists on other sites

3. **Slow response times**
   - Normal for first searches (web scraping takes time)
   - Rate limiting ensures reliability
   - Consider reducing max_retailers in search

### Debug Mode

Enable debug logging by checking bot console for:
```
[Firecrawl] Scraping URL: https://...
Price comparison error: ...
Error searching JB Hi-Fi: ...
```

## Cost Considerations

### Firecrawl API Costs
- Firecrawl charges per page scraped
- Consider implementing caching for frequently searched products
- Monitor usage to stay within budget limits

### Optimization Tips
1. **Limit Retailers**: Reduce `max_retailers` parameter for faster/cheaper searches
2. **Cache Results**: Store search results temporarily to avoid re-scraping
3. **Smart Searching**: Only search when users specifically request comparisons

## Alternative Implementations

If Firecrawl isn't suitable, consider:

1. **Direct Retailer APIs**: Some retailers offer product APIs
2. **Other Scraping Services**: Alternative services like ScrapingBee or Proxycrawl
3. **Browser Automation**: Using Selenium or Playwright (more complex)
4. **RSS/XML Feeds**: Some retailers provide product feeds

## Privacy and Legal Considerations

- Respect retailer robots.txt files
- Implement appropriate rate limiting
- Don't overwhelm retailer servers
- Consider reaching out to retailers for official partnerships
- Ensure compliance with website terms of service

The price comparison feature is now ready to use! Configure Firecrawl to enable full functionality and start helping users find the best deals across Australian retailers.
