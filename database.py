import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        print(f"Initializing database at: {self.db_path}")
        self.init_database()
    
    def fix_missing_timestamps(self):
        """Fix any existing products that have None values for last_checked field"""
        try:
            print("Checking for products with missing timestamps...")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find products with None last_checked
                cursor.execute('''
                    SELECT id FROM products WHERE last_checked IS NULL OR last_checked = ''
                ''')
                rows = cursor.fetchall()
                
                if rows:
                    print(f"Found {len(rows)} products with missing timestamps, fixing...")
                    current_time = datetime.now(timezone.utc)
                    
                    for row in rows:
                        product_id = row[0]
                        cursor.execute('''
                            UPDATE products SET last_checked = ? WHERE id = ?
                        ''', (current_time, product_id))
                        print(f"Fixed timestamp for product {product_id}")
                    
                    conn.commit()
                    print(f"Fixed timestamps for {len(rows)} products")
                else:
                    print("No products with missing timestamps found")
                    
        except Exception as e:
            print(f"Error fixing missing timestamps: {e}")
            import traceback
            traceback.print_exc()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            print(f"Initializing database at: {self.db_path}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table - stores user preferences and store settings
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        preferred_state TEXT,
                        preferred_store_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                print("Users table created/verified")
                
                # Products table - stores tracked products
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        product_code TEXT NOT NULL,
                        product_name TEXT,
                        product_url TEXT,
                        current_price REAL,
                        lowest_price REAL,
                        last_checked TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        UNIQUE(user_id, product_code)
                    )
                ''')
                print("Products table created/verified")
                
                # Price history table - stores price changes
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER NOT NULL,
                        price REAL NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                print("Price history table created/verified")
                
                # Notifications table - stores sent notifications
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        old_price REAL NOT NULL,
                        new_price REAL NOT NULL,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                print("Notifications table created/verified")
                
                conn.commit()
                print("Database initialization completed successfully")
                
                # Fix any existing products with missing timestamps
                self.fix_missing_timestamps()
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def add_user(self, user_id: int, username: str) -> bool:
        """Add a new user to the database"""
        try:
            print(f"Adding user {user_id} ({username}) to database")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                current_time = datetime.now(timezone.utc)
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, updated_at)
                    VALUES (?, ?, ?)
                ''', (user_id, username, current_time))
                conn.commit()
                print(f"Successfully added/updated user {user_id}")
                return True
        except Exception as e:
            print(f"Error adding user: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_user_store(self, user_id: int, state: str, store_id: str = None) -> bool:
        """Update user's preferred store location"""
        try:
            print(f"Updating store preferences for user {user_id}: state={state}, store_id={store_id}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                current_time = datetime.now(timezone.utc)
                cursor.execute('''
                    UPDATE users 
                    SET preferred_state = ?, preferred_store_id = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (state, store_id, current_time, user_id))
                conn.commit()
                print(f"Successfully updated store preferences for user {user_id}")
                return True
        except Exception as e:
            print(f"Error updating user store: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        try:
            print(f"Getting user {user_id} from database")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, preferred_state, preferred_store_id, created_at, updated_at
                    FROM users WHERE user_id = ?
                ''', (user_id,))
                row = cursor.fetchone()
                if row:
                    user = {
                        'user_id': row[0],
                        'username': row[1],
                        'preferred_state': row[2],
                        'preferred_store_id': row[3],
                        'created_at': row[4],
                        'updated_at': row[5]
                    }
                    print(f"Found user: {user}")
                    return user
                else:
                    print(f"User {user_id} not found in database")
                    return None
        except Exception as e:
            print(f"Error getting user: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def add_product(self, user_id: int, product_code: str, product_name: str = None, 
                   product_url: str = None, current_price: float = None) -> bool:
        """Add a new product to track"""
        try:
            print(f"Adding product {product_code} for user {user_id}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if product already exists (regardless of active status)
                if self.product_exists(user_id, product_code):
                    print(f"Product {product_code} already exists for user {user_id}, checking if inactive...")
                    
                    # Check if the product is inactive and reactivate it
                    cursor.execute('''
                        SELECT id, is_active FROM products 
                        WHERE user_id = ? AND LOWER(product_code) = LOWER(?)
                    ''', (user_id, product_code))
                    row = cursor.fetchone()
                    
                    if row and not row[1]:  # Product exists but is inactive
                        product_id = row[0]
                        current_time = datetime.now(timezone.utc)
                        
                        # Reactivate the product and update its information
                        cursor.execute('''
                            UPDATE products 
                            SET product_name = ?, product_url = ?, current_price = ?, lowest_price = ?, 
                                last_checked = ?, is_active = 1
                            WHERE id = ?
                        ''', (product_name, product_url, current_price, current_price, current_time, product_id))
                        
                        conn.commit()
                        print(f"Successfully reactivated product {product_code} for user {user_id}")
                        return True
                    else:
                        print(f"Product {product_code} is already active for user {user_id}")
                        return False
                
                # Product doesn't exist, add new one
                current_time = datetime.now(timezone.utc)
                print(f"Inserting new product with timestamp: {current_time}")
                
                cursor.execute('''
                    INSERT INTO products 
                    (user_id, product_code, product_name, product_url, current_price, lowest_price, last_checked)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, product_code, product_name, product_url, current_price, current_price, current_time))
                conn.commit()
                print(f"Successfully added new product {product_code} for user {user_id}")
                return True
        except Exception as e:
            print(f"Error adding product: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def product_exists(self, user_id: int, product_code: str) -> bool:
        """Check if a product is already tracked by a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM products 
                    WHERE user_id = ? AND LOWER(product_code) = LOWER(?)
                ''', (user_id, product_code))
                count = cursor.fetchone()[0]
                print(f"Product {product_code} exists check for user {user_id}: {count > 0}")
                return count > 0
        except Exception as e:
            print(f"Error checking if product exists: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user_products(self, user_id: int) -> List[Dict]:
        """Get all products tracked by a user"""
        try:
            print(f"Getting products for user {user_id} from database: {self.db_path}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, product_code, product_name, product_url, current_price, lowest_price, last_checked, is_active
                    FROM products WHERE user_id = ? AND is_active = 1
                    ORDER BY COALESCE(last_checked, '1970-01-01 00:00:00') DESC
                ''', (user_id,))
                rows = cursor.fetchall()
                print(f"Found {len(rows)} products for user {user_id}")
                
                products = []
                for i, row in enumerate(rows):
                    try:
                        print(f"Processing row {i}: {row}")
                        product = {
                            'id': row[0],
                            'product_code': row[1],
                            'product_name': row[2],
                            'product_url': row[3],
                            'current_price': row[4],
                            'lowest_price': row[5],
                            'last_checked': row[6],
                            'is_active': row[7]
                        }
                        products.append(product)
                        print(f"Product: {product['product_code']} - Price: {product['current_price']} - Last Check: {product['last_checked']}")
                    except Exception as e:
                        print(f"Error processing product row {i} ({row}): {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                return products
        except Exception as e:
            print(f"Error getting user products: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_product_price(self, product_id: int, new_price: float) -> bool:
        """Update product price and check for price drops"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current product info
                cursor.execute('''
                    SELECT current_price, lowest_price FROM products WHERE id = ?
                ''', (product_id,))
                row = cursor.fetchone()
                if not row:
                    print(f"Product {product_id} not found in database")
                    return False
                
                current_price, lowest_price = row
                print(f"Updating product {product_id}: current_price={current_price}, lowest_price={lowest_price}, new_price={new_price}")
                
                # Update price and lowest price if needed
                new_lowest_price = min(lowest_price, new_price) if lowest_price else new_price
                
                current_time = datetime.now(timezone.utc)
                cursor.execute('''
                    UPDATE products 
                    SET current_price = ?, lowest_price = ?, last_checked = ?
                    WHERE id = ?
                ''', (new_price, new_lowest_price, current_time, product_id))
                
                # Add to price history
                cursor.execute('''
                    INSERT INTO price_history (product_id, price) VALUES (?, ?)
                ''', (product_id, new_price))
                
                conn.commit()
                print(f"Successfully updated product {product_id} price to {new_price}")
                return True
        except Exception as e:
            print(f"Error updating product price: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def remove_product(self, user_id: int, product_code: str) -> bool:
        """Remove a product from tracking (soft delete)"""
        try:
            print(f"Removing product {product_code} for user {user_id}")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE products SET is_active = 0 WHERE user_id = ? AND LOWER(product_code) = LOWER(?)
                ''', (user_id, product_code))
                conn.commit()
                print(f"Successfully removed product {product_code} for user {user_id}")
                return True
        except Exception as e:
            print(f"Error removing product: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_all_active_products(self) -> List[Dict]:
        """Get all active products for price checking"""
        try:
            print("Getting all active products for price checking")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.id, p.user_id, p.product_code, p.current_price, p.lowest_price
                    FROM products p
                    JOIN users u ON p.user_id = u.user_id
                    WHERE p.is_active = 1
                ''')
                rows = cursor.fetchall()
                print(f"Found {len(rows)} active products for price checking")
                return [{
                    'id': row[0],
                    'user_id': row[1],
                    'product_code': row[2],
                    'current_price': row[3],
                    'lowest_price': row[4]
                } for row in rows]
        except Exception as e:
            print(f"Error getting all active products: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def add_notification(self, user_id: int, product_id: int, old_price: float, new_price: float) -> bool:
        """Record a price drop notification"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO notifications (user_id, product_id, old_price, new_price)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, product_id, old_price, new_price))
                conn.commit()
                print(f"Successfully added notification for user {user_id}, product {product_id}")
                return True
        except Exception as e:
            print(f"Error adding notification: {e}")
            import traceback
            traceback.print_exc()
            return False
