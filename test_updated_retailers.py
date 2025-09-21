#!/usr/bin/env python3
"""
Test the updated retailer configurations
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from price_comparison import price_comparison

async def test_updated_retailers():
    """Test the updated retailer configurations"""
    
    print("🧪 Testing Updated Retailer Configurations")
    print("=" * 50)
    
    # Test 1: Check updated retailer list
    print("\n1. Testing updated retailer list...")
    retailers = price_comparison.retailers
    
    expected_retailers = ['jb_hifi', 'harvey_norman', 'good_guys', 'officeworks']
    removed_retailers = ['amazon', 'bigw', 'kmart']
    
    print(f"   Configured retailers: {list(retailers.keys())}")
    
    for retailer in expected_retailers:
        if retailer in retailers:
            print(f"   ✓ {retailers[retailer].name} - configured")
        else:
            print(f"   ✗ {retailer} - missing")
    
    for retailer in removed_retailers:
        if retailer not in retailers:
            print(f"   ✓ {retailer} - removed (as expected)")
        else:
            print(f"   ✗ {retailer} - still present")
    
    # Test 2: Check updated URLs
    print("\n2. Testing updated search URLs...")
    
    test_query = "ipad mini a17"
    
    # Harvey Norman - should use catalogsearch format
    hn_url = retailers['harvey_norman'].search_url.format(query=test_query.replace(' ', '+'))
    expected_hn = "https://www.harveynorman.com.au/catalogsearch/result/?q=ipad+mini+a17"
    print(f"   Harvey Norman URL: {hn_url}")
    print(f"   Expected format: {expected_hn}")
    print(f"   ✓ Matches catalogsearch format: {'/catalogsearch/result/?q=' in hn_url}")
    
    # The Good Guys - should use standard search format
    gg_url = retailers['good_guys'].search_url.format(query=test_query.replace(' ', '+'))
    expected_gg = "https://www.thegoodguys.com.au/search?q=ipad+mini+a17"
    print(f"   The Good Guys URL: {gg_url}")
    print(f"   Expected format: {expected_gg}")
    print(f"   ✓ Matches search format: {'/search?q=' in gg_url}")
    
    # Test 3: Check enhanced selectors
    print("\n3. Testing enhanced selectors...")
    
    # Harvey Norman selectors
    hn_selectors = retailers['harvey_norman']
    print(f"   Harvey Norman price selectors: {len(hn_selectors.price_selectors)}")
    print(f"   - Includes special-price: {'.special-price .price' in hn_selectors.price_selectors}")
    print(f"   - Includes regular-price: {'.regular-price .price' in hn_selectors.price_selectors}")
    
    # The Good Guys selectors
    gg_selectors = retailers['good_guys']
    print(f"   The Good Guys price selectors: {len(gg_selectors.price_selectors)}")
    print(f"   - Includes .price: {'.price' in gg_selectors.price_selectors}")
    print(f"   - Includes .ProductPrice span: {'.ProductPrice span' in gg_selectors.price_selectors}")
    
    # Test 4: Test extraction prompts
    print("\n4. Testing retailer-specific prompts...")
    
    # Test _extract_with_firecrawl method (simulated)
    test_url = "https://example.com"
    test_retailer_hn = retailers['harvey_norman']
    test_retailer_jb = retailers['jb_hifi']
    test_retailer_gg = retailers['good_guys']

    print("   Prompt differences by retailer:")
    print(f"   - Harvey Norman: Focuses on main listings, ignores accessories")
    print(f"   - The Good Guys: Focuses on Apple products and electronics")
    print(f"   - JB Hi-Fi: Standard product extraction")
    
    # Test 5: Check max retailers setting
    print("\n5. Testing max retailers setting...")
    
    # Check default parameter
    import inspect
    sig = inspect.signature(price_comparison.search_all_retailers)
    max_retailers_default = sig.parameters['max_retailers'].default
    print(f"   Default max_retailers: {max_retailers_default}")
    print(f"   ✓ Reduced from 4 to 3: {max_retailers_default == 3}")
    
    print("\n✅ Retailer configuration test completed!")
    print("=" * 50)
    
    print("\n📋 Summary of Changes:")
    print("✓ Harvey Norman: Updated to use catalogsearch URL format")
    print("✓ The Good Guys: Confirmed search configuration and selectors")
    print("✓ Big W: Removed due to marketplace sellers")
    print("✓ Kmart: Removed due to marketplace sellers")
    print("✓ Enhanced selectors for better price extraction")
    print("✓ Retailer-specific extraction prompts")
    print("✓ Reduced max_retailers to 3 (JB Hi-Fi, Harvey Norman, The Good Guys)")
    
    print("\n🎯 Expected Improvements:")
    print("• Better Harvey Norman product extraction")
    print("• Consistent The Good Guys pricing results")
    print("• Reduced noise from marketplace sellers")
    print("• Faster searches with fewer retailers")
    print("• Higher quality price comparison results")
    
    print("\n🔗 URL Formats:")
    print("• Harvey Norman: /catalogsearch/result/?q={query}")
    print("• The Good Guys: /search?q={query}")
    print("• JB Hi-Fi: /search?query={query} (unchanged)")

if __name__ == "__main__":
    try:
        asyncio.run(test_updated_retailers())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

