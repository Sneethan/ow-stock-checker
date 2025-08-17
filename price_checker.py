import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import Database
from officeworks_api import OfficeworksAPI
from colors import *
import discord

class PriceChecker:
    def __init__(self, bot: discord.Client, database: Database, api: OfficeworksAPI):
        self.bot = bot
        self.database = database
        self.api = api
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Start the price checker scheduler"""
        if not self.is_running:
            self.scheduler.add_job(
                self.check_all_prices,
                IntervalTrigger(minutes=30),  # Check every 30 minutes
                id='price_check',
                replace_existing=True
            )
            self.scheduler.start()
            self.is_running = True
            print("Price checker started")
    
    def stop(self):
        """Stop the price checker scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("Price checker stopped")
    
    async def check_all_prices(self):
        """Check prices for all active products"""
        try:
            print(f"Starting price check at {datetime.now(timezone.utc)}")
            
            # Get all active products
            products = self.database.get_all_active_products()
            if not products:
                print("No active products to check")
                return
            
            print(f"Checking prices for {len(products)} products")
            
            # Check each product
            for product in products:
                await self.check_product_price(product)
                # Small delay to avoid overwhelming the API
                await asyncio.sleep(1)
            
            print(f"Price check completed at {datetime.now(timezone.utc)}")
            
        except Exception as e:
            print(f"Error in price check: {e}")
    
    async def check_product_price(self, product: Dict):
        """Check price for a specific product"""
        try:
            product_code = product['product_code']
            product_id = product['id']
            user_id = product['user_id']
            current_price = product['current_price']
            
            print(f"Checking price for product {product_code}")
            
            # Get current price from API
            product_info = self.api.get_product_info(product_code)
            if not product_info or product_info.get('price') is None:
                print(f"Could not get price for product {product_code}")
                return
            
            new_price = product_info['price']
            
            # Update price in database
            if self.database.update_product_price(product_id, new_price):
                print(f"Updated price for {product_code}: ${current_price} -> ${new_price}")
                
                # Check if price dropped
                if current_price and new_price < current_price:
                    await self.send_price_drop_notification(user_id, product_id, product_code, current_price, new_price)
                elif current_price and new_price > current_price:
                    print(f"Price increased for {product_code}: ${current_price} -> ${new_price}")
            else:
                print(f"Failed to update price for {product_code}")
                
        except Exception as e:
            print(f"Error checking product price: {e}")
    
    async def send_price_drop_notification(self, user_id: int, product_id: int, product_code: str, old_price: float, new_price: float):
        """Send price drop notification to user"""
        try:
            # Get user's Discord user object
            user = self.bot.get_user(user_id)
            if not user:
                print(f"Could not find user {user_id} for notification")
                return
            
            # Calculate price drop
            price_drop = old_price - new_price
            price_drop_percentage = (price_drop / old_price) * 100
            
            # Create notification message
            embed = discord.Embed(
                title="💰 Price Drop Alert! 💰",
                description=f"**{product_code.upper()}** price has dropped!",
                color=SUCCESS_COLOR,
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(
                name="Old Price",
                value=f"${old_price:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="New Price",
                value=f"${new_price:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="Savings",
                value=f"${price_drop:.2f} ({price_drop_percentage:.1f}%)",
                inline=True
            )
            
            embed.add_field(
                name="Product Code",
                value=product_code.upper(),
                inline=False
            )
            
            embed.set_footer(text="Officeworks Price Tracker")
            
            # Send DM to user
            try:
                await user.send(embed=embed)
                print(f"Price drop notification sent to user {user_id}")
                
                # Record notification in database
                self.database.add_notification(user_id, product_id, old_price, new_price)
                
            except discord.Forbidden:
                print(f"Cannot send DM to user {user_id} - DMs may be disabled")
            except Exception as e:
                print(f"Error sending notification to user {user_id}: {e}")
                
        except Exception as e:
            print(f"Error in price drop notification: {e}")
    
    async def check_product_now(self, product_code: str, user_id: int) -> Optional[Dict]:
        """Check price for a specific product immediately (for manual checks)"""
        try:
            print(f"Checking product {product_code} for user {user_id}")
            
            # Get product info from API
            product_info = self.api.get_product_info(product_code)
            if not product_info:
                print(f"No product info returned from API for {product_code}")
                return None
            
            print(f"Product info: {product_info}")
            
            # Get user's tracked products
            user_products = self.database.get_user_products(user_id)
            print(f"User products: {user_products}")
            
            tracked_product = next((p for p in user_products if p['product_code'].lower() == product_code.lower()), None)
            print(f"Tracked product: {tracked_product}")
            
            if tracked_product:
                # Update existing product
                old_price = tracked_product['current_price']
                new_price = product_info['price']
                print(f"Updating price: {old_price} -> {new_price}")
                
                try:
                    if self.database.update_product_price(tracked_product['id'], new_price):
                        return {
                            'product_code': product_code,
                            'name': product_info.get('name', 'Unknown'),
                            'old_price': old_price,
                            'new_price': new_price,
                            'price_drop': old_price - new_price if old_price and new_price < old_price else 0,
                            'updated': True
                        }
                    else:
                        print(f"Failed to update product price in database")
                        return None
                except Exception as e:
                    print(f"Error updating product price: {e}")
                    import traceback
                    traceback.print_exc()
                    return None
            else:
                # Product not tracked yet
                print(f"Product {product_code} not tracked by user {user_id}")
                return {
                    'product_code': product_code,
                    'name': product_info.get('name', 'Unknown'),
                    'current_price': product_info.get('price'),
                    'updated': False
                }
                
        except Exception as e:
            print(f"Error in immediate price check: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_next_check_time(self) -> datetime:
        """Get the next scheduled price check time"""
        if not self.is_running:
            return None
        
        job = self.scheduler.get_job('price_check')
        if job:
            return job.next_run_time
        return None
