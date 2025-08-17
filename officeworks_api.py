import requests
import re
from typing import Dict, List, Optional, Tuple
from config import OFFICEWORKS_API_BASE, OFFICEWORKS_HEADERS

class OfficeworksAPI:
    def __init__(self):
        self.base_url = OFFICEWORKS_API_BASE
        self.headers = OFFICEWORKS_HEADERS
    
    def extract_product_code(self, url: str) -> Optional[str]:
        """
        Extract product code from Officeworks URL.
        Takes the last part after the final dash.
        """
        try:
            # Remove trailing slash if present
            url = url.rstrip('/')
            # Split by dash and take the last part
            parts = url.split('-')
            if len(parts) > 1:
                return parts[-1].lower()
            return None
        except Exception as e:
            print(f"Error extracting product code: {e}")
            return None
    
    def get_product_info(self, product_code: str) -> Optional[Dict]:
        """
        Get product information from Officeworks API
        """
        try:
            url = f"{self.base_url}/stock-check/product/{product_code}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'id': data.get('id'),
                    'name': data.get('name'),
                    'description': data.get('description'),
                    'url': data.get('urlPath'),
                    'image': data.get('image'),
                    'price': float(data.get('price', 0)) if data.get('price') else None
                }
            else:
                print(f"API request failed with status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Error getting product info: {e}")
            return None
    
    def get_store_availability(self, product_code: str, state: str) -> Optional[Dict]:
        """
        Get store availability for a product in a specific state
        """
        try:
            url = f"{self.base_url}/stock-check/product/{product_code}/availability/{state.lower()}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'states': data.get('states', []),
                    'stores': data.get('stores', [])
                }
            else:
                print(f"Store availability request failed with status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Error getting store availability: {e}")
            return None
    
    def get_stores_in_state(self, state: str) -> List[Dict]:
        """
        Get all stores in a specific state
        """
        try:
            # Use a common product to get store list
            url = f"{self.base_url}/stock-check/product/ipdmw128g/availability/{state.lower()}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                stores = data.get('stores', [])
                
                # Format store information
                formatted_stores = []
                for store in stores:
                    formatted_stores.append({
                        'store_id': store.get('storeId'),
                        'name': store.get('store'),
                        'address': store.get('address'),
                        'suburb': store.get('suburb'),
                        'postcode': store.get('postcode'),
                        'state': store.get('state'),
                        'phone': store.get('phone'),
                        'longitude': store.get('longitude'),
                        'latitude': store.get('latitude')
                    })
                
                return formatted_stores
            else:
                print(f"Store list request failed with status {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []
        except Exception as e:
            print(f"Error getting stores in state: {e}")
            return []
    
    def validate_product_url(self, url: str) -> bool:
        """
        Validate if a URL is a valid Officeworks product URL
        """
        try:
            # Check if it's an Officeworks URL
            if not url.startswith('https://www.officeworks.com.au/shop/officeworks/p/'):
                return False
            
            # Check if it has a product code at the end
            product_code = self.extract_product_code(url)
            if not product_code:
                return False
            
            # Try to get product info to validate
            product_info = self.get_product_info(product_code)
            return product_info is not None
            
        except Exception as e:
            print(f"Error validating product URL: {e}")
            return False
    
    def get_product_by_url(self, url: str) -> Optional[Dict]:
        """
        Get product information by URL
        """
        try:
            product_code = self.extract_product_code(url)
            if not product_code:
                return None
            
            return self.get_product_info(product_code)
            
        except Exception as e:
            print(f"Error getting product by URL: {e}")
            return None
