#!/usr/bin/env python3
"""
Test script for database functionality
Run this to verify the database is working before starting the bot
"""

from database import Database
from datetime import datetime

def test_database():
    """Test the database functionality"""
    print("🗄️  Testing Database Integration...")
    print("=" * 50)
    
    try:
        db = Database()
        print("✓ Database connection successful")
        
        # Test 1: Add user
        print("\n1. Testing user management...")
        test_user_id = 12345
        test_username = "TestUser"
        
        if db.add_user(test_user_id, test_username):
            print("   ✓ User added successfully")
        else:
            print("   ❌ Failed to add user")
            return False
        
        # Test 2: Get user
        user = db.get_user(test_user_id)
        if user and user['username'] == test_username:
            print("   ✓ User retrieved successfully")
        else:
            print("   ❌ Failed to retrieve user")
            return False
        
        # Test 3: Update user store
        if db.update_user_store(test_user_id, "VIC", "W346"):
            print("   ✓ User store updated successfully")
        else:
            print("   ❌ Failed to update user store")
            return False
        
        # Test 4: Add product
        print("\n2. Testing product management...")
        test_product_code = "TEST123"
        test_product_name = "Test Product"
        
        if db.add_product(
            user_id=test_user_id,
            product_code=test_product_code,
            product_name=test_product_name,
            current_price=99.99
        ):
            print("   ✓ Product added successfully")
        else:
            print("   ❌ Failed to add product")
            return False
        
        # Test 5: Get user products
        products = db.get_user_products(test_user_id)
        if products and len(products) > 0:
            print(f"   ✓ Retrieved {len(products)} product(s)")
            test_product = products[0]
            print(f"   Product: {test_product['product_name']} (${test_product['current_price']:.2f})")
        else:
            print("   ❌ Failed to retrieve products")
            return False
        
        # Test 6: Update product price
        if db.update_product_price(test_product['id'], 89.99):
            print("   ✓ Product price updated successfully")
        else:
            print("   ❌ Failed to update product price")
            return False
        
        # Test 7: Get all active products
        all_products = db.get_all_active_products()
        if all_products and len(all_products) > 0:
            print(f"   ✓ Retrieved {len(all_products)} active product(s)")
        else:
            print("   ❌ Failed to retrieve all active products")
            return False
        
        # Test 8: Remove product
        if db.remove_product(test_user_id, test_product_code):
            print("   ✓ Product removed successfully")
        else:
            print("   ❌ Failed to remove product")
            return False
        
        print("\n" + "=" * 50)
        print("🎯 Database Test Complete!")
        print("✅ All tests passed! The database is working correctly.")
        print("   You can now run the Discord bot.")
        
        return True
        
    except Exception as e:
        print(f"\n💥 Database test failed with error: {e}")
        print("   Please check your setup and try again.")
        return False

if __name__ == "__main__":
    try:
        success = test_database()
        if success:
            print("\n🚀 Ready to start the bot!")
        else:
            print("\n⚠️  Please fix the database issues before starting the bot.")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        print("   Please check your setup and try again.")
    
    input("\nPress Enter to exit...")
