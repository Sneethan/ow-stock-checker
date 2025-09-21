import asyncio
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import discord
from colors import *
from emojis import *

class RetailerConfig:
    """Configuration for a specific retailer"""
    def __init__(self, name: str, base_url: str, search_url: str, price_selectors: List[str], 
                 title_selectors: List[str], link_selectors: List[str] = None, 
                 price_match_threshold: float = 0.95):
        self.name = name
        self.base_url = base_url
        self.search_url = search_url
        self.price_selectors = price_selectors
        self.title_selectors = title_selectors
        self.link_selectors = link_selectors or []
        self.price_match_threshold = price_match_threshold

class PriceComparison:
    """Price comparison across multiple retailers using Firecrawl"""
    
    def __init__(self, firecrawl_client=None):
        self.firecrawl_client = firecrawl_client
        self.retailers = self._setup_retailers()
    
    def _setup_retailers(self) -> Dict[str, RetailerConfig]:
        """Setup configuration for different retailers"""
        return {
            'jb_hifi': RetailerConfig(
                name="JB Hi-Fi",
                base_url="https://www.jbhifi.com.au",
                search_url="https://www.jbhifi.com.au/search?query={query}",
                price_selectors=[
                    '.price-current',
                    '.price .price-value',
                    '.pricing .current-price',
                    '.price-now',
                    '[data-testid="price"]',
                    '.ProductPrice__price',
                    '.ProductPrice__price span',
                    '.ProductTile__Price',
                    '[data-component="ProductPrice"]'
                ],
                title_selectors=[
                    '.product-title',
                    '.product-name',
                    'h1.title',
                    '.product-heading',
                    '[data-testid="product-title"]',
                    '.ProductTile__Title',
                    '[data-component="ProductName"]'
                ],
                link_selectors=[
                    '.product-item a',
                    '.product-card a',
                    '.product-link',
                    '.ProductTile__Body a'
                ],
                price_match_threshold=0.3  # Lower threshold for better matching
            ),
            'harvey_norman': RetailerConfig(
                name="Harvey Norman",
                base_url="https://www.harveynorman.com.au",
                search_url="https://www.harveynorman.com.au/catalogsearch/result/?q={query}",
                price_selectors=[
                    '.price-current',
                    '.current-price',
                    '.price .now',
                    '.pricing-price',
                    '.price-display',
                    '.special-price .price',
                    '.regular-price .price',
                    '.price-box .price',
                    '.price-container span.price'
                ],
                title_selectors=[
                    '.product-title',
                    '.product-name',
                    'h1.heading',
                    '.product-heading',
                    '.product-item-name',
                    'h2.product-name',
                    '.product-item-link'
                ],
                link_selectors=[
                    '.product-tile a',
                    '.product-item a',
                    '.product-item-link'
                ],
                price_match_threshold=0.3
            ),
            'amazon': RetailerConfig(
                name="Amazon AU",
                base_url="https://www.amazon.com.au",
                search_url="https://www.amazon.com.au/s?k={query}&ref=nb_sb_noss",
                price_selectors=[
                    '.a-price-whole',
                    '.a-price .a-offscreen',
                    '.a-price-symbol + .a-price-whole',
                    '.price .a-price-whole',
                    '.a-price-amount .a-offscreen',
                    '.sx-price .a-offscreen',
                    '.a-row .a-price .a-offscreen'
                ],
                title_selectors=[
                    '[data-cy="title-recipe"]',
                    '.a-size-medium.a-color-base',
                    '.s-size-mini .a-color-base',
                    'h2 .a-link-normal .a-text-normal',
                    '.s-link-style .a-text-normal',
                    'h3.s-size-mini span',
                    '.a-text-normal.a-color-base.a-size-base-plus'
                ],
                link_selectors=[
                    '[data-cy="title-recipe"] a',
                    '.s-product-image-container a',
                    '.a-link-normal',
                    '.s-link-style'
                ],
                price_match_threshold=0.3
            ),
            'good_guys': RetailerConfig(
                name="The Good Guys",
                base_url="https://www.thegoodguys.com.au",
                search_url="https://www.thegoodguys.com.au/search?q={query}",
                price_selectors=[
                    '.price',
                    '.product-price',
                    '.current-price',
                    '.sale-price',
                    '.price-current',
                    '.pricing .price',
                    '.pricing .price-now',
                    '.ProductPrice span'
                ],
                title_selectors=[
                    '.product-title',
                    '.product-name',
                    'h3.product-title',
                    'h4.product-title',
                    '.product-item-name',
                    '.title',
                    '.ProductName'
                ],
                link_selectors=[
                    '.product-tile a',
                    '.product-item a',
                    '.product-link',
                    'a.product-title',
                    '.ProductCard a'
                ],
                price_match_threshold=0.3
            ),
            'officeworks': RetailerConfig(
                name="Officeworks",
                base_url="https://www.officeworks.com.au",
                search_url="https://www.officeworks.com.au/shop/SearchDisplay?searchTerm={query}",
                price_selectors=[
                    '.price-current',
                    '.product-price .price',
                    '.current-price',
                    '.price-display'
                ],
                title_selectors=[
                    '.product-title',
                    '.product-name',
                    'h1.title'
                ],
                link_selectors=[
                    '.product-item a',
                    '.product-card a'
                ]
            )
        }
    
    async def search_all_retailers(self, product_name: str, officeworks_price: float, 
                                 max_retailers: int = 4) -> List[Dict]:
        """Search all configured retailers for price comparisons"""
        if not self.firecrawl_client:
            return []
        
        results = []
        search_query = self._clean_product_name(product_name)
        
        # Search each retailer (excluding Officeworks since we already have that price)
        retailers_to_search = [r for name, r in self.retailers.items() if name != 'officeworks']
        
        # Limit the number of retailers to search to avoid API limits
        retailers_to_search = retailers_to_search[:max_retailers]
        
        for retailer in retailers_to_search:
            try:
                retailer_result = await self._search_retailer(retailer, search_query, officeworks_price)
                if retailer_result:
                    results.append(retailer_result)
                
                # Add small delay between searches
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error searching {retailer.name}: {e}")
                continue
        
        return results
    
    async def _search_retailer(self, retailer: RetailerConfig, query: str, 
                             officeworks_price: float) -> Optional[Dict]:
        """Search a specific retailer for the product using Firecrawl Extract"""
        try:
            search_url = retailer.search_url.format(query=query.replace(' ', '+'))
            
            # Try using Firecrawl Extract first for better structured data
            extract_result = await self._extract_with_firecrawl(search_url, retailer, query)
            
            if extract_result and extract_result.get('success'):
                products = extract_result.get('data', {}).get('products', [])
                
                # Debug output
                print(f"[Debug Extract] {retailer.name}: Extracted {len(products)} products using Extract")
                for i, product in enumerate(products[:3]):
                    print(f"[Debug Extract] Product {i+1}: {product.get('name', 'No name')[:80]}... - ${product.get('price', 'No price')}")
                
                if products:
                    # Convert extract format to our internal format
                    formatted_products = []
                    for product in products:
                        formatted_products.append({
                            'title': product.get('name', product.get('title', '')),
                            'price': self._parse_price(product.get('price', 0)),
                            'url': product.get('url', search_url),
                            'availability': product.get('availability', 'unknown'),
                            'brand': product.get('brand', ''),
                            'model': product.get('model', '')
                        })
                    
                    # Find the best matching product
                    best_match = self._find_best_product_match(formatted_products, query, retailer.price_match_threshold)
                    
                    if best_match:
                        print(f"[Debug Extract] {retailer.name}: Found match using Extract - {best_match.get('title', 'No title')[:80]} - ${best_match.get('price')}")
                        
                        # Calculate price difference and match eligibility
                        price_difference = officeworks_price - best_match['price']
                        is_cheaper = best_match['price'] < officeworks_price
                        
                        return {
                            'retailer': retailer.name,
                            'product_name': best_match['title'],
                            'price': best_match['price'],
                            'url': best_match.get('url', search_url),
                            'price_difference': abs(price_difference),
                            'is_cheaper': is_cheaper,
                            'potential_savings': price_difference if is_cheaper else 0,
                            'price_match_eligible': is_cheaper and price_difference >= 0.01,
                            'extraction_method': 'firecrawl_extract'
                        }
            
            # Fallback to traditional scraping if Extract fails
            print(f"[Debug] {retailer.name}: Extract failed, falling back to traditional scraping")
            response = await self._scrape_with_firecrawl(search_url, retailer)
            
            if not response:
                return None
            
            # Extract products from the response
            products = self._extract_products_from_response(response, retailer)
            
            # Debug output
            print(f"[Debug] {retailer.name}: Extracted {len(products)} products from search")
            for i, product in enumerate(products[:3]):  # Show first 3 for debugging
                print(f"[Debug] Product {i+1}: {product.get('title', 'No title')[:80]}... - ${product.get('price', 'No price')}")
            
            if not products:
                print(f"[Debug] {retailer.name}: No products extracted from response")
                return None
            
            # Find the best matching product
            best_match = self._find_best_product_match(products, query, retailer.price_match_threshold)
            
            # Debug output for matching
            if best_match:
                print(f"[Debug] {retailer.name}: Found match - {best_match.get('title', 'No title')[:80]} - ${best_match.get('price')}")
            else:
                print(f"[Debug] {retailer.name}: No suitable match found from {len(products)} products")
                print(f"[Debug] Query: '{query}', Threshold: {retailer.price_match_threshold}")
            
            if not best_match:
                return None
            
            # Check if this price offers a potential price match
            price_difference = officeworks_price - best_match['price']
            is_cheaper = best_match['price'] < officeworks_price
            
            return {
                'retailer': retailer.name,
                'product_name': best_match['title'],
                'price': best_match['price'],
                'url': best_match.get('url', search_url),
                'price_difference': abs(price_difference),
                'is_cheaper': is_cheaper,
                'potential_savings': price_difference if is_cheaper else 0,
                'price_match_eligible': is_cheaper and price_difference >= 0.01,  # At least 1 cent difference
                'extraction_method': 'traditional_scraping'
            }
            
        except Exception as e:
            print(f"Error searching {retailer.name}: {e}")
            return None
    
    async def _extract_with_firecrawl(self, url: str, retailer: RetailerConfig, query: str) -> Optional[Dict]:
        """Use Firecrawl Extract to get structured product data"""
        try:
            if not self.firecrawl_client:
                return None
            
            # Create a schema for product extraction
            product_schema = {
                "type": "object",
                "properties": {
                    "products": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Product name or title"},
                                "price": {"type": ["string", "number"], "description": "Product price in dollars"},
                                "url": {"type": "string", "description": "Product page URL"},
                                "availability": {"type": "string", "description": "Stock availability status"},
                                "brand": {"type": "string", "description": "Product brand"},
                                "model": {"type": "string", "description": "Product model number"}
                            },
                            "required": ["name", "price"]
                        }
                    }
                },
                "required": ["products"]
            }
            
            # Create a specific prompt for this retailer and query
            if retailer.name == "Amazon AU":
                prompt = f"""Extract product information from this Amazon Australia search results page for "{query}". 
                Focus on genuine Apple products or exact product matches, ignore cases, accessories, and third-party items unless specifically relevant.
                Look for products with prices in AUD ($). Extract the product name, price (as a number without currency symbols), product URL, availability status, brand, and model.
                Ignore "Renewed" products unless specifically searching for them.
                Return up to 8 most relevant products."""
            elif retailer.name == "Harvey Norman":
                prompt = f"""Extract product information from this Harvey Norman search results page for "{query}". 
                Focus on main product listings, ignore accessories unless specifically relevant.
                Look for products with clear pricing. Extract the product name, price (as a number without currency symbols), product URL, availability status, brand, and model.
                Return up to 10 most relevant products."""
            elif retailer.name == "The Good Guys":
                prompt = f"""Extract product information from this The Good Guys search results page for "{query}". 
                Focus on main Apple products and electronics, ignore cases, accessories, and extended warranties unless specifically relevant.
                Look for products with clear pricing in AUD ($). Extract the product name, price (as a number without currency symbols), product URL, availability status, brand, and model.
                Return up to 10 most relevant products."""
            else:
                prompt = f"""Extract product information from this {retailer.name} search results page for "{query}". 
                Focus on products that match the search term "{query}". 
                Extract the product name, price (as a number without currency symbols), product URL, availability status, brand, and model if available.
                Return up to 10 most relevant products."""
            
            # Use the extract_products method from firecrawl integration
            result = await self.firecrawl_client.extract_products(url, prompt=prompt, schema=product_schema)
            
            return result
            
        except Exception as e:
            print(f"Error in Firecrawl Extract for {retailer.name}: {e}")
            return None
    
    def _parse_price(self, price_value) -> float:
        """Parse price from various formats to float"""
        try:
            if isinstance(price_value, (int, float)):
                return float(price_value)
            
            if isinstance(price_value, str):
                # Remove currency symbols and common price formatting
                price_str = price_value.replace('$', '').replace(',', '').replace('AUD', '').strip()
                
                # Handle price ranges (take the first price)
                if '-' in price_str:
                    price_str = price_str.split('-')[0].strip()
                
                # Handle "from" prices
                if price_str.lower().startswith('from'):
                    price_str = price_str[4:].strip()
                
                # Extract just the number
                import re
                price_match = re.search(r'(\d+(?:\.\d{2})?)', price_str)
                if price_match:
                    return float(price_match.group(1))
            
            return 0.0
            
        except (ValueError, AttributeError):
            return 0.0
    
    async def _scrape_with_firecrawl(self, url: str, retailer: RetailerConfig) -> Optional[Dict]:
        """Use Firecrawl to scrape a retailer's search page"""
        try:
            if not self.firecrawl_client:
                print("Firecrawl client not configured")
                return None
            
            # Note: Scraping options are now configured globally in the Firecrawl client
            # The scrape_url method only takes the URL as an argument
            
            response = await self.firecrawl_client.scrape_url(url)
            return response
            
        except Exception as e:
            print(f"Firecrawl scraping error for {url}: {e}")
            return None
    
    def _extract_products_from_response(self, response: Dict, retailer: RetailerConfig) -> List[Dict]:
        """Extract product information from Firecrawl response"""
        products = []
        
        try:
            # Get both markdown and HTML content if available
            markdown_content = response.get('markdown', '')
            html_content = response.get('html', '')
            
            # Debug output
            print(f"[Debug] {retailer.name}: Markdown length: {len(markdown_content)}, HTML length: {len(html_content)}")
            
            # Try to extract products from markdown first (usually cleaner)
            if markdown_content:
                markdown_products = self._extract_from_markdown(markdown_content, retailer)
                products.extend(markdown_products)
                print(f"[Debug] {retailer.name}: Extracted {len(markdown_products)} products from markdown")
            
            # If no products found in markdown, try HTML
            if not products and html_content:
                html_products = self._extract_from_html(html_content, retailer)
                products.extend(html_products)
                print(f"[Debug] {retailer.name}: Extracted {len(html_products)} products from HTML")

        except Exception as e:
            print(f"Error extracting products: {e}")

        deduplicated = self._deduplicate_products(products)
        print(f"[Debug] {retailer.name}: {len(deduplicated)} products after deduplication")
        return deduplicated
    
    def _extract_from_markdown(self, markdown: str, retailer: RetailerConfig) -> List[Dict]:
        """Extract products from markdown content"""
        products = []
        
        try:
            # Enhanced price patterns to catch more formats
            price_patterns = [
                r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $99.99, $1,999.99 format
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*dollars?',  # 99.99 dollars format
                r'AUD\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # AUD $99.99 format
                r'Price:?\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Price: $99.99
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*AUD',  # 99.99 AUD
                r'From\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # From $99.99
                r'Now\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Now $99.99
            ]
            
            lines = markdown.split('\n')
            current_product = {}
            products_found = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Look for product titles in various formats
                title_found = False
                
                # Headers (## ### etc)
                if re.match(r'^#{1,6}\s+', line) and len(line) > 15:
                    title = re.sub(r'^#{1,6}\s+', '', line).strip()
                    title = re.sub(r'[*\[\]]+', '', title).strip()
                    if len(title) > 8:
                        current_product['title'] = title
                        title_found = True
                
                # Bold text **text**
                elif '**' in line and len(line) > 15:
                    # Extract text between ** markers
                    bold_matches = re.findall(r'\*\*([^*]+)\*\*', line)
                    for bold_text in bold_matches:
                        if len(bold_text) > 8:
                            current_product['title'] = bold_text.strip()
                            title_found = True
                            break
                
                # Link text [text](url) - sometimes product names are in links
                elif '[' in line and '](' in line:
                    link_matches = re.findall(r'\[([^\]]+)\]\([^)]+\)', line)
                    for link_text in link_matches:
                        if len(link_text) > 8 and not link_text.lower().startswith(('http', 'www', 'click', 'view', 'see')):
                            current_product['title'] = link_text.strip()
                            title_found = True
                            break
                
                # Lines that look like product names (no special formatting)
                elif not title_found and 20 <= len(line) <= 150:
                    # Check if it contains product-like words
                    product_indicators = ['router', 'mesh', 'wifi', 'wireless', 'system', 'pack', 'kit', 
                                        'laptop', 'tablet', 'phone', 'headphones', 'camera', 'monitor']
                    if any(indicator in line.lower() for indicator in product_indicators):
                        current_product['title'] = line.strip()
                        title_found = True
                
                # Look for prices in the current line and nearby lines
                for pattern in price_patterns:
                    price_matches = re.findall(pattern, line, re.IGNORECASE)
                    for price_str in price_matches:
                        try:
                            # Remove commas and convert to float
                            clean_price = price_str.replace(',', '')
                            price = float(clean_price)
                            if 5 <= price <= 15000:  # Reasonable price range
                                current_product['price'] = price
                                
                                # If we have a title, save the product
                                if 'title' in current_product:
                                    product_to_save = current_product.copy()
                                    products_found.append(product_to_save)
                                    current_product = {}
                                    break
                        except ValueError:
                            continue
                
                # Look for URLs
                url_matches = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
                for text, url in url_matches:
                    if retailer.base_url in url or 'product' in url.lower():
                        full_url = url if url.startswith('http') else retailer.base_url + url
                        current_product['url'] = full_url
            
            # Also try to extract products from table-like structures
            table_products = self._extract_from_table_structure(markdown, retailer)
            products_found.extend(table_products)
            
            # Remove duplicates based on title similarity
            unique_products = []
            for product in products_found:
                is_duplicate = False
                for existing in unique_products:
                    if self._titles_similar(product.get('title', ''), existing.get('title', '')):
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_products.append(product)
                        
        except Exception as e:
            print(f"Error parsing markdown: {e}")
        
        return unique_products[:15]  # Increased limit for better results
    
    def _extract_from_table_structure(self, markdown: str, retailer: RetailerConfig) -> List[Dict]:
        """Extract products from table-like markdown structures"""
        products = []
        
        try:
            # Look for pipe-separated tables
            lines = markdown.split('\n')
            for line in lines:
                if '|' in line and len(line.split('|')) >= 3:
                    parts = [part.strip() for part in line.split('|') if part.strip()]
                    
                    # Try to identify which part is the product name and which is the price
                    for i, part in enumerate(parts):
                        # Check if this part looks like a price
                        price_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', part)
                        if price_match:
                            try:
                                price = float(price_match.group(1).replace(',', ''))
                                if 5 <= price <= 15000:
                                    # Look for a product name in other parts
                                    for j, other_part in enumerate(parts):
                                        if i != j and len(other_part) > 10 and not re.search(r'\$\d', other_part):
                                            products.append({
                                                'title': other_part.strip(),
                                                'price': price,
                                                'url': retailer.base_url
                                            })
                                            break
                            except ValueError:
                                continue
                                
        except Exception as e:
            print(f"Error parsing table structure: {e}")
        
        return products
    
    def _titles_similar(self, title1: str, title2: str) -> bool:
        """Check if two titles are similar enough to be considered duplicates"""
        if not title1 or not title2:
            return False
        
        # Simple similarity check
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        # If they share more than 70% of words, consider them similar
        if len(words1) > 0 and len(words2) > 0:
            overlap = len(words1.intersection(words2))
            similarity = overlap / min(len(words1), len(words2))
            return similarity > 0.7
        
        return False
    
    def _extract_from_html(self, html: str, retailer: RetailerConfig) -> List[Dict]:
        """Extract products from HTML content using retailer specific selectors."""
        products: List[Dict] = []

        try:
            price_patterns = [
                r'class="[^"]*price[^"]*"[^>]*>\s*\$?([\d,.]+)',
                r'data-price="([\d,.]+)"',
                r'\$\s*([\d,.]+)'
            ]
            price_patterns.extend(self._selectors_to_regex(retailer.price_selectors, capture='price'))

            title_patterns = [
                r'<h[1-6][^>]*>([^<]+)</h[1-6]>',
                r'class="[^"]*title[^"]*"[^>]*>([^<]+)<',
                r'class="[^"]*name[^"]*"[^>]*>([^<]+)<'
            ]
            title_patterns.extend(self._selectors_to_regex(retailer.title_selectors, capture='text'))

            link_patterns = self._selectors_to_regex(retailer.link_selectors, capture='link')

            all_prices: List[float] = []
            for pattern in price_patterns:
                prices = re.findall(pattern, html, re.IGNORECASE)
                for price_str in prices:
                    parsed_price = self._parse_price(price_str)
                    if 1 <= parsed_price <= 10000:
                        all_prices.append(parsed_price)

            all_titles: List[str] = []
            for pattern in title_patterns:
                titles = re.findall(pattern, html, re.IGNORECASE)
                for title in titles:
                    clean_title = re.sub(r'<[^>]+>', '', title).strip()
                    if clean_title and len(clean_title) > 5:
                        all_titles.append(clean_title)

            all_links: List[str] = []
            for pattern in link_patterns:
                links = re.findall(pattern, html, re.IGNORECASE)
                for link in links:
                    if isinstance(link, tuple):
                        link = link[-1]
                    link = link.strip()
                    if link:
                        all_links.append(self._build_absolute_url(link, retailer.base_url))

            min_items = min(len(all_prices), len(all_titles))
            for index in range(min_items):
                url = all_links[index] if index < len(all_links) else retailer.base_url
                products.append({
                    'title': all_titles[index],
                    'price': all_prices[index],
                    'url': url
                })

        except Exception as e:
            print(f"Error parsing HTML: {e}")

        return products[:5]

    def _selectors_to_regex(self, selectors: List[str], capture: str) -> List[str]:
        """Convert CSS-like selectors into lightweight regex patterns."""
        patterns: List[str] = []

        for selector in selectors or []:
            selector = selector.strip()
            if not selector:
                continue

            if selector.startswith('[') and '=' in selector:
                attr, _, remainder = selector[1:-1].partition('=')
                attr = attr.strip()
                cleaned = remainder.strip()
                value = cleaned.strip('"').strip("'")
                if capture == 'price':
                    patterns.append(rf'{attr}\s*=\s*"{re.escape(value)}"[^>]*>[^$]*\$?([\d,.]+)')
                elif capture == 'link':
                    patterns.append(rf'{attr}\s*=\s*"{re.escape(value)}"[^>]*href="([^"]+)"')
                else:
                    patterns.append(rf'{attr}\s*=\s*"{re.escape(value)}"[^>]*>([^<]+)<')
                continue

            tag = '[^>]*'
            class_name = ''
            if '.' in selector:
                parts = selector.split('.')
                if parts[0]:
                    tag = parts[0]
                class_name = parts[-1]
            elif selector.startswith('.'):  # pure class selector
                class_name = selector[1:]
            else:
                tag = selector

            class_pattern = r''
            if class_name:
                class_pattern = rf'class="[^"]*{re.escape(class_name)}[^"]*"'

            if capture == 'price':
                patterns.append(rf'<{tag}[^>]*{class_pattern}[^>]*>[^$]*\$?([\d,.]+)')
            elif capture == 'link':
                patterns.append(rf'<{tag}[^>]*{class_pattern}[^>]*href="([^"]+)"')
            else:
                patterns.append(rf'<{tag}[^>]*{class_pattern}[^>]*>([^<]+)<')

        return patterns

    def _build_absolute_url(self, candidate_url: str, base_url: str) -> str:
        """Ensure URLs are absolute for downstream Discord embeds."""
        if candidate_url.startswith('http'):
            return candidate_url
        if candidate_url.startswith('//'):
            return f'https:{candidate_url}'
        if candidate_url.startswith('/'):
            return f"{base_url.rstrip('/')}{candidate_url}"
        return f"{base_url.rstrip('/')}/{candidate_url.lstrip('/')}"

    def _deduplicate_products(self, products: List[Dict]) -> List[Dict]:
        """Remove duplicate listings based on normalized title and price."""
        seen = set()
        deduped: List[Dict] = []

        for product in products:
            title = product.get('title')
            price = self._parse_price(product.get('price'))
            if not title or price <= 0:
                continue

            normalized_title = self._normalize_text(title)
            dedupe_key = (normalized_title, round(price, 2))

            if dedupe_key in seen:
                continue

            seen.add(dedupe_key)
            product['price'] = price
            deduped.append(product)

        return deduped
    
    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        normalized = re.sub(r'[^a-z0-9]+', ' ', text.lower())
        return ' '.join(normalized.split())

    def _calculate_match_score(self, query_normalized: str, product: Dict,
                               key_terms: List[str], query_words: set) -> float:
        title = product.get('title', '')
        normalized_title = self._normalize_text(title)
        if not normalized_title:
            return 0.0

        title_words = set(normalized_title.split())
        price = self._parse_price(product.get('price', 0))

        score = 0.0

        # Overall similarity between normalized strings
        if query_normalized:
            similarity_ratio = SequenceMatcher(None, query_normalized, normalized_title).ratio()
            score += similarity_ratio * 0.35

        # Key term coverage (brands, tech keywords, model numbers)
        if key_terms:
            matches = sum(1 for term in key_terms if term in normalized_title)
            score += (matches / len(key_terms)) * 0.2

        # Word overlap
        if query_words:
            overlap = len(query_words.intersection(title_words)) / len(query_words)
            score += overlap * 0.25

        # Partial matches for specs/model numbers
        if query_words:
            partial_matches = 0
            for query_word in query_words:
                if len(query_word) < 3:
                    continue
                for title_word in title_words:
                    if query_word in title_word or title_word in query_word:
                        partial_matches += 1
                        break
            score += (partial_matches / len(query_words)) * 0.1

        # Number alignment (capacities, model numbers)
        query_numbers = re.findall(r'\d+', query_normalized)
        title_numbers = re.findall(r'\d+', normalized_title)
        if query_numbers:
            number_matches = len(set(query_numbers).intersection(set(title_numbers)))
            score += (number_matches / len(query_numbers)) * 0.05

        # Bonus for explicit brand/model metadata when provided
        product_brand = self._normalize_text(product.get('brand', ''))
        if product_brand and product_brand in query_normalized:
            score += 0.03

        product_model = self._normalize_text(product.get('model', ''))
        if product_model and product_model in query_normalized:
            score += 0.03

        # Price sanity check to avoid zero-value matches
        if 1 <= price <= 10000:
            score += 0.02

        # Reasonable title length tends to indicate a proper listing
        title_length = len(title_words)
        if 3 <= title_length <= 15:
            score += 0.02

        return min(score, 1.0)

    def _find_best_product_match(self, products: List[Dict], query: str,
                               threshold: float) -> Optional[Dict]:
        """Find the best matching product from search results using fuzzy matching"""
        if not products:
            return None

        query_normalized = self._normalize_text(query)
        query_words = set(query_normalized.split())
        key_terms = self._extract_key_terms(query_normalized)

        candidate_scores: List[Tuple[float, float, Dict]] = []
        for product in products:
            price = self._parse_price(product.get('price'))
            if price <= 0:
                continue

            product['price'] = price
            score = self._calculate_match_score(query_normalized, product, key_terms, query_words)
            if score <= 0:
                continue

            candidate_scores.append((score, price, product))

        if not candidate_scores:
            return None

        # Prioritise the most similar product, break ties by lowest price.
        candidate_scores.sort(key=lambda item: (-item[0], item[1]))

        min_score = max(threshold, 0.2)
        for score, _, product in candidate_scores:
            if score >= min_score:
                return product

        # Fall back to a slightly more permissive threshold if nothing met the requirement
        for score, _, product in candidate_scores:
            if score >= 0.15:
                return product

        return candidate_scores[0][2] if candidate_scores else None
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms (brands, model numbers, important features) from query"""
        key_terms = []
        words = query.split()
        
        # Common tech brands
        brands = [
            'tp-link', 'tplink', 'apple', 'samsung', 'sony', 'lg', 'hp', 'dell', 'lenovo',
            'asus', 'acer', 'microsoft', 'google', 'amazon', 'netgear', 'linksys',
            'cisco', 'nvidia', 'intel', 'amd', 'logitech', 'razer', 'corsair', 'belkin'
        ]
        
        # Important tech terms
        tech_terms = [
            'wifi', 'mesh', 'router', 'modem', 'wireless', 'ethernet', 'bluetooth',
            'usb', 'hdmi', 'laptop', 'desktop', 'tablet', 'phone', 'headphones',
            'speaker', 'camera', 'monitor', 'keyboard', 'mouse', 'gaming'
        ]
        
        # Extract brands and tech terms
        for word in words:
            word_clean = word.lower().strip()
            if word_clean in brands or word_clean in tech_terms:
                key_terms.append(word_clean)
        
        # Extract model numbers (words with numbers and letters)
        import re
        for word in words:
            if re.search(r'[a-zA-Z]\d|\d[a-zA-Z]', word):  # Contains both letters and numbers
                key_terms.append(word.lower())
        
        # Extract capacity/size numbers
        for word in words:
            if re.match(r'\d+(gb|tb|mg|kg|inch|"|\')', word.lower()):
                key_terms.append(word.lower())
        
        return list(set(key_terms))  # Remove duplicates
    
    def _clean_product_name(self, product_name: str) -> str:
        """Clean product name for better search results"""
        if not product_name:
            return ""
        
        # Remove common words that might interfere with search
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        
        # Remove brand-specific terms that might not exist on other sites
        brand_terms = {'officeworks', 'exclusive', 'limited', 'special', 'edition'}
        
        # Clean up the name
        clean_name = re.sub(r'[^\w\s-]', ' ', product_name.lower())
        words = [word for word in clean_name.split() 
                if word not in stop_words and word not in brand_terms and len(word) > 2]
        
        return ' '.join(words[:8])  # Limit to 8 most relevant words
    
    def create_comparison_embed(self, product_name: str, officeworks_price: float, 
                              comparisons: List[Dict]) -> discord.Embed:
        """Create a Discord embed showing price comparisons"""
        
        # Filter to only show retailers with better prices or close matches
        relevant_comparisons = [
            comp for comp in comparisons 
            if comp['is_cheaper'] or comp['price_difference'] <= (officeworks_price * 0.1)
        ]
        
        if not relevant_comparisons:
            embed = discord.Embed(
                title=f"{PRICE} Price Comparison Results",
                description=f"No better prices found for **{product_name}**",
                color=INFO_COLOR
            )
            embed.add_field(
                name=f"{STORE} Officeworks Price",
                value=f"${officeworks_price:.2f}",
                inline=True
            )
            embed.add_field(
                name="Status",
                value=f"{SUCCESS} Best price found!",
                inline=True
            )
            return embed
        
        # Sort by potential savings (highest first)
        relevant_comparisons.sort(key=lambda x: x['potential_savings'], reverse=True)
        
        embed = discord.Embed(
            title=f"{COMPARE} Price Comparison Results",
            description=f"Found price comparisons for **{product_name}**",
            color=WARNING_COLOR if any(c['is_cheaper'] for c in relevant_comparisons) else SUCCESS_COLOR
        )
        
        # Add Officeworks price at the top
        embed.add_field(
            name=f"{STORE} Officeworks",
            value=f"${officeworks_price:.2f}",
            inline=True
        )
        
        # Add comparison results
        for i, comp in enumerate(relevant_comparisons[:4]):  # Limit to 4 competitors
            if comp['is_cheaper']:
                value = f"${comp['price']:.2f} {PRICE_DROP}\n**Save ${comp['potential_savings']:.2f}!**"
                if comp['price_match_eligible']:
                    value += f"\n{SUCCESS} Price match eligible!"
            else:
                value = f"${comp['price']:.2f}\n+${comp['price_difference']:.2f} more"
            
            # Add extraction method indicator for enhanced results
            if comp.get('extraction_method') == 'firecrawl_extract':
                value += "\n🔍 AI Enhanced"
            
            embed.add_field(
                name=f"{EXTERNAL_LINK} {comp['retailer']}",
                value=value,
                inline=True
            )
        
        # Add price match information
        cheapest = min(relevant_comparisons, key=lambda x: x['price'], default=None)
        if cheapest and cheapest['price_match_eligible']:
            embed.add_field(
                name=f"{PRICE_MATCH} Price Match Opportunity",
                value=f"Show **{cheapest['retailer']}** price (${cheapest['price']:.2f}) to Officeworks for a potential price match!",
                inline=False
            )
        
        embed.set_footer(text="Prices may vary. Check retailer websites for current pricing.")
        embed.timestamp = datetime.now(timezone.utc)
        
        return embed

# Initialize a global instance (will be configured with Firecrawl in bot)
price_comparison = PriceComparison()
