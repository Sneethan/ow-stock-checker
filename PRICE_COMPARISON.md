# Price Comparison Feature

## Overview

The Officeworks Stock Checker bot now includes a comprehensive price comparison feature that allows users to compare prices across multiple Australian retailers. This feature helps users identify potential price matching opportunities and find the best deals.

## Supported Retailers

The price comparison system currently supports the following retailers:

- **JB Hi-Fi** - Electronics and entertainment
- **Harvey Norman** - Electronics and appliances  
- **Amazon AU** - Wide range of products
- **Officeworks** - Office supplies and electronics

*Note: Big W and Kmart were removed due to prevalence of marketplace sellers affecting price accuracy.*

## How It Works

### 1. Firecrawl Integration

The system uses Firecrawl to extract product data from retailer websites. Firecrawl provides:
- **Extract Feature**: Structured data extraction using LLMs and schemas
- JavaScript rendering for dynamic content
- Clean markdown and HTML extraction as fallback
- Rate limiting and error handling
- Content filtering for main product information

### 2. Price Extraction

For each retailer, the system:
- **Primary**: Uses Firecrawl Extract with structured schemas for precise data
- **Fallback**: Traditional markdown/HTML parsing if Extract fails  
- Searches using cleaned product names
- Extracts product titles, prices, and availability
- Matches products based on enhanced similarity scores
- Identifies the best matching products

### 3. Price Match Detection

The system analyzes prices to identify:
- Products cheaper than Officeworks
- Potential price match opportunities
- Savings amounts and percentages
- Products within a reasonable price range

## Commands

### /check with Price Comparison

Enhanced the existing `/check` command with an optional price comparison parameter:

```
/check product_code:ipdmw128g compare_prices:True
```

**Parameters:**
- `product_code` - The Officeworks product code to check
- `compare_prices` - Boolean flag to enable price comparison (default: False)

**Behavior:**
1. Checks the current Officeworks price
2. If `compare_prices` is True, searches other retailers
3. Shows a comparison embed with potential savings
4. Highlights price match opportunities

### /compare - Standalone Price Comparison

New command for comparing prices without tracking:

```
/compare search_query:"iPad Mini 128GB"
/compare search_query:ipdmw128g officeworks_price:899.00
```

**Parameters:**
- `search_query` - Product name, description, or Officeworks product code
- `officeworks_price` - Optional Officeworks price for comparison

**Behavior:**
1. If no Officeworks price provided, tries to extract from product code
2. Searches all configured retailers
3. Shows comprehensive price comparison
4. Provides search suggestions if no results found

## Price Match Opportunities

The system identifies potential price match scenarios by:

### Eligibility Criteria
- Product found at competing retailer
- Competitor price is lower than Officeworks price
- Price difference is at least $0.01
- Product similarity score meets threshold

### Price Match Alerts
When price match opportunities are found, the bot displays:
- 🎯 Price match eligible indicator
- Exact savings amount
- Retailer name and price
- Instructions for price matching

### Example Output
```
⚖️ Price Comparison Results
Found price comparisons for iPad Mini 128GB

🏪 Officeworks: $899.00

🔗 JB Hi-Fi: $849.00 📉
Save $50.00!
✅ Price match eligible!

🔗 Harvey Norman: $879.00
Save $20.00!
✅ Price match eligible!

🎯 Price Match Opportunity
Show JB Hi-Fi price ($849.00) to Officeworks for a potential price match!
```

## Configuration

### Retailer Configuration

Each retailer is configured with:

```python
RetailerConfig(
    name="JB Hi-Fi",
    base_url="https://www.jbhifi.com.au",
    search_url="https://www.jbhifi.com.au/search?query={query}",
    price_selectors=['.price-current', '.price .price-value'],
    title_selectors=['.product-title', '.product-name'],
    link_selectors=['.product-item a'],
    price_match_threshold=0.95
)
```

### Search Optimization

Product names are cleaned for better search results:
- Remove common stop words
- Remove brand-specific terms
- Limit to relevant keywords
- Handle special characters

### Rate Limiting

The system implements rate limiting:
- 2-second delay between retailer searches
- 1-second delay between individual requests
- Maximum 4-5 retailers per search
- Error handling for failed requests

## Setup and Configuration

### Firecrawl Setup

1. **Install Firecrawl MCP** (if using Cursor environment):
   ```bash
   # Firecrawl MCP should be available in Cursor
   ```

2. **Alternative: Direct API Integration**:
   ```bash
   pip install firecrawl-py
   ```
   
   Then configure API key in environment:
   ```
   FIRECRAWL_API_KEY=your_api_key_here
   ```

### Bot Configuration

The price comparison is automatically initialized when the bot starts:

```python
# In bot.py
from price_comparison import price_comparison
from firecrawl_integration import firecrawl_integration

# Configure price comparison with Firecrawl
price_comparison.firecrawl_client = firecrawl_integration
```

## Error Handling

The system handles various error scenarios:

### Firecrawl Unavailable
- Falls back to informational message
- Suggests configuration steps
- Continues with Officeworks price check

### Retailer Search Failures
- Skips failed retailers
- Continues with successful ones
- Logs errors for debugging

### No Results Found
- Provides search suggestions
- Shows alternative search terms
- Maintains user-friendly messaging

### Rate Limiting
- Implements delays between requests
- Handles 429 responses gracefully
- Limits concurrent searches

## Limitations

### Current Limitations
1. **Scraping Dependencies**: Relies on retailer website structure
2. **Product Matching**: May not find exact matches for all products
3. **Price Accuracy**: Prices may not reflect current promotions
4. **Regional Availability**: Limited to Australian retailers

### Future Enhancements
1. **API Integrations**: Direct retailer API connections where available
2. **Machine Learning**: Improved product matching algorithms
3. **More Retailers**: Expand to additional Australian retailers
4. **Price History**: Track competitor price changes over time

## Usage Examples

### Basic Price Check with Comparison
```
User: /check product_code:ipdmw128g compare_prices:True
Bot: 
✅ Price Check Complete
iPad Mini A17 Pro 8.3" WiFi 128GB Space Grey price has been updated!

Product Code: IPDMW128G
Current Price: $899.00
Status: Price unchanged

⚖️ Price Comparison Results
Found price comparisons for iPad Mini A17 Pro 8.3" WiFi 128GB Space Grey

🏪 Officeworks: $899.00
🔗 JB Hi-Fi: $849.00 📉 Save $50.00! ✅ Price match eligible!
🔗 Amazon AU: $869.00 📉 Save $30.00! ✅ Price match eligible!

🎯 Price Match Opportunity
Show JB Hi-Fi price ($849.00) to Officeworks for a potential price match!
```

### Standalone Comparison Search
```
User: /compare search_query:"Sony WH-1000XM4"
Bot:
🔄 Searching retailers for Sony WH-1000XM4...
No Officeworks price provided - showing all found prices

⚖️ Retailer Price Search Results
Found prices for Sony WH-1000XM4 across retailers

🔗 JB Hi-Fi: $348.00
🔗 Harvey Norman: $399.00
🔗 Amazon AU: $329.00
🔗 Big W: $369.00
```

## Troubleshooting

### Common Issues

1. **No Results Found**
   - Try shorter, more generic search terms
   - Check spelling and product names
   - Use brand/model numbers instead of full names

2. **Slow Response Times**
   - Normal for first-time searches
   - Subsequent searches may be faster
   - Rate limiting ensures reliability

3. **Firecrawl Errors**
   - Check Firecrawl configuration
   - Verify API keys if using direct integration
   - Check network connectivity

### Debug Information

Enable debug logging by checking bot console output for:
- `[Firecrawl] Scraping URL: ...`
- `Price comparison error: ...`
- `Error searching {retailer}: ...`

## Privacy and Ethics

### Data Handling
- No personal data stored from retailer searches
- Product information temporarily cached during comparison
- Respects retailer robots.txt and rate limits

### Responsible Scraping
- Implements appropriate delays
- Uses Firecrawl's ethical scraping practices
- Focuses on publicly available product information
- Respects website terms of service

## Support

For issues with the price comparison feature:

1. Check the bot's status with `/status`
2. Try simpler search terms
3. Verify Firecrawl configuration
4. Check bot logs for error messages
5. Report persistent issues to the bot administrator

The price comparison feature enhances the Officeworks Stock Checker by providing valuable market intelligence for better purchasing decisions.
