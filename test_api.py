#!/usr/bin/env python3
"""
Test script for Officeworks API integration
Run this to verify the API is working before starting the bot
"""

import asyncio
from officeworks_api import OfficeworksAPI

def test_api():
    """Test the Officeworks API functionality"""
    print("🧪 Testing Officeworks API Integration...")
    print("=" * 50)
    
    api = OfficeworksAPI()
    
    # Test 1: Extract product code from URL
    print("\n1. Testing URL parsing...")
    test_url = "https://www.officeworks.com.au/shop/officeworks/p/ipad-mini-a17-pro-8-3-wifi-128gb-space-grey-ipdmw128g"
    product_code = api.extract_product_code(test_url)
    print(f"   URL: {test_url}")
    print(f"   Extracted code: {product_code}")
    print(f"   ✓ Success" if product_code == "ipdmw128g" else "   ❌ Failed")
    
    # Test 2: Get product info
    print("\n2. Testing product info retrieval...")
    if product_code:
        product_info = api.get_product_info(product_code)
        if product_info:
            print(f"   Product: {product_info.get('name', 'Unknown')}")
            print(f"   Price: ${product_info.get('price', 0):.2f}")
            print(f"   ✓ Success")
        else:
            print("   ❌ Failed to get product info")
    
    # Test 3: Get stores in VIC
    print("\n3. Testing store retrieval...")
    stores = api.get_stores_in_state("VIC")
    if stores:
        print(f"   Found {len(stores)} stores in VIC")
        if len(stores) > 0:
            print(f"   First store: {stores[0]['name']} ({stores[0]['store_id']})")
        print(f"   ✓ Success")
    else:
        print("   ❌ Failed to get stores")
    
    # Test 4: Validate product URL
    print("\n4. Testing URL validation...")
    is_valid = api.validate_product_url(test_url)
    print(f"   URL valid: {is_valid}")
    print(f"   ✓ Success" if is_valid else "   ❌ Failed")
    
    print("\n" + "=" * 50)
    print("🎯 API Test Complete!")
    
    if product_code and product_info and stores and is_valid:
        print("✅ All tests passed! The API is working correctly.")
        print("   You can now run the Discord bot.")
    else:
        print("❌ Some tests failed. Please check your internet connection")
        print("   and ensure the Officeworks API is accessible.")
    
    return product_code and product_info and stores and is_valid

if __name__ == "__main__":
    try:
        success = test_api()
        if success:
            print("\n🚀 Ready to start the bot!")
        else:
            print("\n⚠️  Please fix the issues before starting the bot.")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        print("   Please check your setup and try again.")
    
    input("\nPress Enter to exit...")
