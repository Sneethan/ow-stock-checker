#!/usr/bin/env python3
"""
Test script for stores data functionality
"""

import json
from config import AUSTRALIAN_STATES, STATE_NAMES

def test_stores_data():
    """Test loading and parsing stores data"""
    try:
        # Load stores data
        with open('responses/allstores.md', 'r', encoding='utf-8') as f:
            content = f.read()
            data = json.loads(content)
        
        print("✅ Successfully loaded stores data")
        print(f"📊 Total stores: {len(data.get('stores', []))}")
        
        # Test state filtering
        for state in AUSTRALIAN_STATES:
            stores_in_state = [s for s in data.get('stores', []) if s['state'] == state]
            print(f"🏪 {STATE_NAMES.get(state, state)}: {len(stores_in_state)} stores")
        
        # Test store details
        if data.get('stores'):
            sample_store = data['stores'][0]
            print(f"\n📋 Sample store:")
            print(f"   Name: {sample_store.get('store', 'N/A')}")
            print(f"   ID: {sample_store.get('storeId', 'N/A')}")
            print(f"   State: {sample_store.get('state', 'N/A')}")
            print(f"   Address: {sample_store.get('address', 'N/A')}")
            print(f"   Suburb: {sample_store.get('suburb', 'N/A')}")
            print(f"   Postcode: {sample_store.get('postcode', 'N/A')}")
            print(f"   Phone: {sample_store.get('phone', 'N/A')}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_stores_data()
