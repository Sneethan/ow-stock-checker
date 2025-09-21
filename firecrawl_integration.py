import asyncio
import inspect
import json
import os
from typing import Dict, Optional, List, Tuple
from datetime import datetime

class FirecrawlIntegration:
    """Integration wrapper for Firecrawl Python SDK"""
    
    def __init__(self):
        self.rate_limit_delay = 2  # Delay between requests to avoid rate limiting
        self.last_request_time = None
        self.firecrawl_app = None
        self.default_request_options = self._build_default_request_options()
        self._initialize_firecrawl()

    def _build_default_request_options(self) -> Dict:
        """Return Firecrawl options recommended for reliable, live scraping."""
        # Firecrawl's documentation highlights these options for forcing live
        # scrapes and improving success rates on dynamic retail pages. We make
        # them available in several naming conventions so the SDK can accept
        # whichever variant it expects without failing the request.
        page_options = {
            "maxAge": 0,
            "timeout": 60000,
            "waitFor": 3000,
            "onlyMainContent": False,
        }

        return {
            "pageOptions": page_options,
            # Duplicate the most important options at the top level in case the
            # SDK expects snake_case argument names instead of nested objects.
            "maxAge": page_options["maxAge"],
            "timeout": page_options["timeout"],
            "waitFor": page_options["waitFor"],
            "onlyMainContent": page_options["onlyMainContent"],
            "proxy": "auto",
        }
    
    def _initialize_firecrawl(self):
        """Initialize the Firecrawl client"""
        try:
            from firecrawl import FirecrawlApp
            
            # Get API key from environment
            api_key = os.getenv('FIRECRAWL_API_KEY')
            
            if api_key:
                # Initialize with just the API key - options will be handled per-request
                self.firecrawl_app = FirecrawlApp(api_key=api_key)
                print(f"[Firecrawl] Successfully initialized with API key")
                
                # Debug: Check what methods are available
                available_methods = [method for method in dir(self.firecrawl_app) if not method.startswith('_')]
                print(f"[Firecrawl] Available methods: {available_methods}")
                
                # Debug: Check method signatures for key methods
                if hasattr(self.firecrawl_app, 'extract'):
                    import inspect
                    try:
                        sig = inspect.signature(self.firecrawl_app.extract)
                        print(f"[Firecrawl] Extract method signature: {sig}")
                    except:
                        print(f"[Firecrawl] Could not get extract method signature")
                
                if hasattr(self.firecrawl_app, 'scrape'):
                    import inspect
                    try:
                        sig = inspect.signature(self.firecrawl_app.scrape)
                        print(f"[Firecrawl] Scrape method signature: {sig}")
                    except:
                        print(f"[Firecrawl] Could not get scrape method signature")
                
                if hasattr(self.firecrawl_app, 'scrape_url'):
                    import inspect
                    try:
                        sig = inspect.signature(self.firecrawl_app.scrape_url)
                        print(f"[Firecrawl] Scrape_url method signature: {sig}")
                    except:
                        print(f"[Firecrawl] Could not get scrape_url method signature")
            else:
                print(f"[Firecrawl] No API key found in FIRECRAWL_API_KEY environment variable")
                self.firecrawl_app = None
                
        except ImportError:
            print(f"[Firecrawl] firecrawl-py package not installed. Run: pip install firecrawl-py")
            self.firecrawl_app = None
        except Exception as e:
            print(f"[Firecrawl] Error initializing Firecrawl: {e}")
            self.firecrawl_app = None
        
    async def _apply_rate_limit(self):
        """Apply rate limiting between requests"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = datetime.now()
    
    def _filter_kwargs_for_signature(self, method, base_kwargs: Dict[str, object]) -> Dict[str, object]:
        """Return kwargs supported by the Firecrawl method signature."""
        try:
            signature = inspect.signature(method)
        except (TypeError, ValueError):
            return base_kwargs

        filtered_kwargs = {}
        for key, value in base_kwargs.items():
            if key in signature.parameters:
                filtered_kwargs[key] = value
        return filtered_kwargs

    def _build_option_kwargs(self, method) -> Dict[str, object]:
        """Build option kwargs supported by the Firecrawl method."""
        try:
            signature = inspect.signature(method)
        except (TypeError, ValueError):
            return {}

        option_kwargs: Dict[str, object] = {}
        params = signature.parameters
        page_options = self.default_request_options.get("pageOptions", {})

        # Firecrawl python client has historically exposed several different
        # argument names, so we proactively support the common variants.
        if "options" in params:
            option_kwargs["options"] = self.default_request_options
        if "page_options" in params:
            option_kwargs["page_options"] = page_options
        if "pageOptions" in params:
            option_kwargs["pageOptions"] = page_options
        if "max_age" in params:
            option_kwargs["max_age"] = page_options.get("maxAge")
        if "maxAge" in params:
            option_kwargs["maxAge"] = page_options.get("maxAge")
        if "timeout" in params:
            option_kwargs["timeout"] = page_options.get("timeout")
        if "wait_for" in params:
            option_kwargs["wait_for"] = page_options.get("waitFor")
        if "waitFor" in params:
            option_kwargs["waitFor"] = page_options.get("waitFor")
        if "only_main_content" in params:
            option_kwargs["only_main_content"] = page_options.get("onlyMainContent")
        if "onlyMainContent" in params:
            option_kwargs["onlyMainContent"] = page_options.get("onlyMainContent")
        if "proxy" in params:
            option_kwargs["proxy"] = self.default_request_options.get("proxy")

        return option_kwargs

    def _call_firecrawl_method(self, method_names: List[str], base_kwargs: Dict[str, object]) -> Tuple[Optional[object], Optional[str]]:
        """Attempt to call one of the provided Firecrawl methods with fallbacks."""
        if not self.firecrawl_app:
            return None, None

        last_error: Optional[Exception] = None

        for method_name in method_names:
            method = getattr(self.firecrawl_app, method_name, None)
            if not method:
                continue

            prepared_kwargs = self._filter_kwargs_for_signature(method, base_kwargs)
            option_kwargs = self._build_option_kwargs(method)

            try:
                return method(**{**prepared_kwargs, **option_kwargs}), method_name
            except TypeError as type_error:
                # Retry without extra options; some SDK releases do not accept
                # them even if the signature appears to allow arbitrary kwargs.
                try:
                    return method(**prepared_kwargs), method_name
                except Exception as secondary_error:  # pragma: no cover - logged below
                    last_error = secondary_error
                    print(f"[Firecrawl] {method_name} failed after retry: {secondary_error}")
            except Exception as error:  # pragma: no cover - logged below
                last_error = error
                print(f"[Firecrawl] {method_name} raised {error}")

        if last_error:
            raise last_error

        return None, None

    async def extract_products(self, url: str, prompt: str = None, schema: Dict = None) -> Optional[Dict]:
        """
        Use Firecrawl's Extract feature to get structured product data
        
        Args:
            url: The URL to extract from
            prompt: Natural language prompt for extraction
            schema: JSON schema for structured data
            
        Returns:
            Dictionary containing extracted structured data
        """
        try:
            await self._apply_rate_limit()
            
            if not self.firecrawl_app:
                print(f"[Firecrawl Extract] Firecrawl not configured - returning mock data")
                return {
                    'success': False,
                    'error': 'Firecrawl not configured',
                    'data': []
                }
            
            # Default prompt for product extraction if none provided
            if not prompt and not schema:
                prompt = "Extract product information including name, price, and availability from this retail page."
            
            print(f"[Firecrawl Extract] Extracting from URL: {url}")
            
            try:
                # Use the extract method with either prompt or schema
                # The extract method should handle the parameters correctly
                print(f"[Firecrawl Extract] Calling extract with url={url}, prompt={prompt is not None}, schema={schema is not None}")
                
                # Check if the extract method exists
                base_kwargs = {
                    'urls': [url],
                    'url': url,
                }

                if schema:
                    print(f"[Firecrawl Extract] Using schema-based extraction")
                    base_kwargs['schema'] = schema
                elif prompt:
                    print(f"[Firecrawl Extract] Using prompt-based extraction")
                    base_kwargs['prompt'] = prompt

                result, method_used = self._call_firecrawl_method(['extract'], base_kwargs)

                if method_used:
                    print(f"[Firecrawl Extract] Called method '{method_used}' with enhanced options")
                else:
                    print(f"[Firecrawl Extract] No extract method available on FirecrawlApp")
                    return {
                        'success': False,
                        'error': 'Extract method not found on FirecrawlApp',
                        'url': url
                    }
                
                print(f"[Firecrawl Extract] Extract result: {result}")
                
                # Handle the response object properly
                if hasattr(result, 'success') and result.success:
                    print(f"[Firecrawl Extract] Successfully extracted from {url}")
                    return {
                        'success': True,
                        'data': result.data if hasattr(result, 'data') else {},
                        'url': url
                    }
                else:
                    error_msg = getattr(result, 'error', 'Unknown error') if result else 'No result returned'
                    print(f"[Firecrawl Extract] Failed to extract from {url}: {error_msg}")
                    return {
                        'success': False,
                        'error': str(error_msg),
                        'url': url
                    }
                    
            except Exception as e:
                print(f"[Firecrawl Extract] Exception during extraction {url}: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'url': url
                }
            
        except Exception as e:
            print(f"[Firecrawl Extract] Error extracting {url}: {e}")
            return None

    async def scrape_url(self, url: str) -> Optional[Dict]:
        """
        Scrape a single URL using Firecrawl Python SDK
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing scraped content or None if failed
        """
        try:
            await self._apply_rate_limit()
            
            if not self.firecrawl_app:
                print(f"[Firecrawl] Firecrawl not configured - returning mock data")
                return {
                    'success': False,
                    'error': 'Firecrawl not configured',
                    'markdown': f'# Mock data for {url}\n\nFirecrawl needs configuration.',
                    'html': '<div>Mock response - Configure Firecrawl API key</div>',
                    'url': url
                }
            
            print(f"[Firecrawl] Scraping URL: {url}")

            # Use the Firecrawl Python SDK with the resilient option handling
            try:
                base_kwargs = {
                    'url': url,
                    'urls': [url],
                }

                result, method_used = self._call_firecrawl_method(['scrape', 'scrape_url'], base_kwargs)

                if not method_used:
                    print(f"[Firecrawl] Warning: Could not find scrape method on FirecrawlApp")
                    return {
                        'success': False,
                        'error': 'Scrape method not found on FirecrawlApp',
                        'url': url
                    }

                print(f"[Firecrawl] Using {method_used} with enhanced options")

                # Handle the response object properly
                if hasattr(result, 'success') and result.success:
                    print(f"[Firecrawl] Successfully scraped {url}")
                    return {
                        'success': True,
                        'markdown': getattr(result, 'markdown', ''),
                        'html': getattr(result, 'html', ''),
                        'url': url
                    }
                else:
                    error_msg = getattr(result, 'error', 'Unknown error') if result else 'No result returned'
                    print(f"[Firecrawl] Failed to scrape {url}: {error_msg}")
                    return {
                        'success': False,
                        'error': str(error_msg),
                        'url': url
                    }
                    
            except Exception as e:
                print(f"[Firecrawl] Exception during scraping {url}: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'url': url
                }
            
        except Exception as e:
            print(f"[Firecrawl] Error scraping {url}: {e}")
            return None
    
    async def search_retailer(self, retailer_name: str, search_query: str, 
                            retailer_config: Dict) -> Optional[Dict]:
        """
        Search a specific retailer for products
        
        Args:
            retailer_name: Name of the retailer
            search_query: Search terms
            retailer_config: Configuration for the retailer
            
        Returns:
            Dictionary containing search results
        """
        try:
            search_url = retailer_config['search_url'].format(
                query=search_query.replace(' ', '+')
            )
            
            # Note: Options are now configured globally in the constructor
            # For search results, we'll use the default configuration
            
            result = await self.scrape_url(search_url)
            
            if result and result.get('success'):
                return {
                    'retailer': retailer_name,
                    'search_query': search_query,
                    'search_url': search_url,
                    'content': result
                }
            else:
                print(f"[Firecrawl] Failed to search {retailer_name}")
                return None
                
        except Exception as e:
            print(f"[Firecrawl] Error searching {retailer_name}: {e}")
            return None
    
    async def batch_search_retailers(self, retailers: List[Dict], search_query: str) -> List[Dict]:
        """
        Search multiple retailers in batch
        
        Args:
            retailers: List of retailer configurations
            search_query: Search terms
            
        Returns:
            List of search results from each retailer
        """
        results = []
        
        for retailer in retailers:
            try:
                result = await self.search_retailer(
                    retailer['name'], 
                    search_query, 
                    retailer
                )
                
                if result:
                    results.append(result)
                
                # Add delay between retailer searches
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"[Firecrawl] Error in batch search for {retailer.get('name', 'unknown')}: {e}")
                continue
        
        return results
    
    def is_available(self) -> bool:
        """Check if Firecrawl integration is available"""
        return self.firecrawl_app is not None
    
    async def test_connection(self) -> Dict:
        """Test the Firecrawl connection"""
        try:
            if not self.is_available():
                return {
                    'success': False,
                    'error': 'Firecrawl not configured',
                    'message': 'Please install firecrawl-py and set FIRECRAWL_API_KEY environment variable'
                }
            
            # Test with a simple URL
            test_result = await self.scrape_url('https://httpbin.org/json')
            
            if test_result and test_result.get('success'):
                return {
                    'success': True,
                    'message': 'Firecrawl connection successful'
                }
            else:
                error_msg = test_result.get('error', 'Unknown error') if test_result else 'No result'
                return {
                    'success': False,
                    'error': error_msg,
                    'message': 'Firecrawl API test failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error testing Firecrawl connection'
            }

# Global instance
firecrawl_integration = FirecrawlIntegration()
