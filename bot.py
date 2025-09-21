import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import signal
import sys
from datetime import datetime, timezone
from typing import Optional

import json
from config import BOT_TOKEN, AUSTRALIAN_STATES, STATE_NAMES, USE_EPHEMERAL_MESSAGES, get_relative_timestamp, get_future_relative_time, get_full_timestamp
from colors import *
from emojis import *
from database import Database
from officeworks_api import OfficeworksAPI
from price_checker import PriceChecker
from price_comparison import price_comparison
from firecrawl_integration import firecrawl_integration

class StoreSetupError(Exception):
    """Raised when a user's store preferences cannot be saved."""


def _build_store_options(stores):
    """Create Discord select options for the provided stores."""
    options = []
    for store in stores[:25]:
        store_id = store.get('storeId')
        if not store_id:
            continue

        suburb = store.get('suburb', '')
        postcode = store.get('postcode', '')
        suburb_postcode = f"{suburb}, {postcode}".strip(', ')
        description = f"{suburb_postcode} - ID: {store_id}" if suburb_postcode else f"ID: {store_id}"

        options.append(
            discord.SelectOption(
                label=store.get('store', 'Unknown Store'),
                value=store_id,
                description=description
            )
        )
    return options


class StateSelectionView(discord.ui.View):
    """View for selecting Australian state/territory"""
    
    def __init__(self, bot: 'OfficeworksBot'):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        
        # Create select menu for states
        self.add_item(StateSelect(bot))

class StateSelect(discord.ui.Select):
    """Select menu for Australian states"""
    
    def __init__(self, bot: 'OfficeworksBot'):
        self.bot = bot
        
        # Create options for all Australian states
        options = []
        for state_code in AUSTRALIAN_STATES:
            state_name = STATE_NAMES.get(state_code, state_code)
            options.append(
                discord.SelectOption(
                    label=state_name,
                    value=state_code,
                    description=f"Select {state_name} for store preferences"
                )
            )
        
        super().__init__(
            placeholder="Choose your state/territory...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle state selection"""
        try:
            selected_state = self.values[0]
            
            # Create store selection view
            view = StoreSelectionView(self.bot, selected_state)
            await interaction.response.edit_message(
                content=f"{STORE} **Store Setup - {STATE_NAMES.get(selected_state, selected_state)}**\n\n"
                        f"Please select your preferred store (or choose 'Any store'):",
                view=view
            )
            
        except Exception as e:
            print(f"Error in state selection: {e}")
            await interaction.response.edit_message(
                content=f"{ERROR} An error occurred. Please try again.",
                view=None
            )

class StoreSelectionView(discord.ui.View):
    """View for selecting specific store or any store"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str):
        super().__init__(timeout=300)
        self.bot = bot
        self.state = state
        
        # Add "Any store" option
        self.add_item(AnyStoreButton(bot, state))
        
        # Add store search with autocomplete
        self.add_item(StoreSearchSelect(bot, state))
        
        # Add search button for better store search
        self.add_item(StoreSearchButton(bot, state))
        
        # Add "Browse stores" option
        self.add_item(BrowseStoresButton(bot, state))
        
        # Add "Back to states" option
        self.add_item(BackToStatesButton(bot))

class AnyStoreButton(discord.ui.Button):
    """Button to select any store in the state"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str):
        self.bot = bot
        self.state = state
        
        super().__init__(
            label=f"{STORE} Any Store in State",
            style=discord.ButtonStyle.primary,
            emoji=SUCCESS
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle any store selection"""
        try:
            await self._complete_setup(interaction, self.state, None)
        except Exception as e:
            print(f"Error in any store selection: {e}")
            await interaction.response.edit_message(
                content=f"{ERROR} An error occurred. Please try again.",
                view=None
            )
    
    async def _complete_setup(self, interaction: discord.Interaction, state: str, store_id: str = None):
        """Complete the setup process"""
        user_id = interaction.user.id
        username = interaction.user.display_name

        try:
            embed = self.bot.complete_store_setup(
                user_id,
                username,
                state,
                store_id=store_id
            )
        except StoreSetupError as exc:
            await interaction.response.edit_message(
                content=f"{ERROR} {exc}",
                view=None
            )
            return

        await interaction.response.edit_message(content=None, embed=embed, view=None)

class BrowseStoresButton(discord.ui.Button):
    """Button to browse available stores"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str):
        self.bot = bot
        self.state = state
        
        super().__init__(
            label=f"{SEARCH} Browse Stores",
            style=discord.ButtonStyle.secondary,
            emoji=f"{BROWSE}"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Show store list"""
        try:
            await interaction.response.defer(ephemeral=USE_EPHEMERAL_MESSAGES)
            
            stores = self.bot.get_stores_by_state(self.state)
            if not stores:
                await interaction.followup.send(
                    f"{ERROR} No stores found in {self.state}.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            # Create store selection view
            view = SpecificStoreView(self.bot, self.state, stores)
            await interaction.followup.send(
                f"{STORE} **Available Stores in {STATE_NAMES.get(self.state, self.state)}**\n\n"
                f"Found {len(stores)} stores. Select one or go back:",
                view=view,
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
            
        except Exception as e:
            print(f"Error browsing stores: {e}")
            await interaction.followup.send(
                f"{ERROR} An error occurred while fetching stores.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )

class BackToStatesButton(discord.ui.Button):
    """Button to go back to state selection"""
    
    def __init__(self, bot: 'OfficeworksBot'):
        self.bot = bot
        
        super().__init__(
            label=f"{BACK_ARROW} Back to States",
            style=discord.ButtonStyle.danger,
            emoji=f"{BACK_ICON}"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Go back to state selection"""
        try:
            view = StateSelectionView(self.bot)
            await interaction.response.edit_message(
                content=f"{STORE} **Officeworks Store Setup**\n\n"
                        "Please select your preferred state/territory:",
                view=view
            )
        except Exception as e:
            print(f"Error going back to states: {e}")
            await interaction.response.edit_message(
                content=f"{ERROR} An error occurred. Please try again.",
                view=None
            )

class SpecificStoreView(discord.ui.View):
    """View for selecting a specific store"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str, stores: list):
        super().__init__(timeout=300)
        self.bot = bot
        self.state = state
        self.stores = stores
        
        # Add store selection dropdown
        self.add_item(StoreSelect(bot, state, stores))
        
        # Add back button
        self.add_item(BackToStoreSelectionButton(bot, state))

class StoreSelect(discord.ui.Select):
    """Select menu for specific stores"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str, stores: list):
        self.bot = bot
        self.state = state
        
        options = _build_store_options(stores)
        has_options = bool(options)
        if not has_options:
            options = [
                discord.SelectOption(
                    label="No stores available",
                    value="no_stores",
                    description="Use the back button to try again."
                )
            ]
        super().__init__(
            placeholder="Choose your preferred store...",
            min_values=1,
            max_values=1,
            options=options
        )

        if not has_options:
            self.disabled = True
    
    async def callback(self, interaction: discord.Interaction):
        """Handle store selection"""
        try:
            selected_store_id = self.values[0]
            if selected_store_id == "no_stores":
                await interaction.response.send_message(
                    f"{ERROR} No stores available. Please try again later.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            selected_store = self.bot.get_store_by_id(selected_store_id)

            if selected_store:
                await self._complete_setup(interaction, self.state, selected_store_id, selected_store)
            else:
                await interaction.response.edit_message(
                    content=f"{ERROR} Store not found. Please try again.",
                    view=None
                )
                
        except Exception as e:
            print(f"Error in store selection: {e}")
            await interaction.response.edit_message(
                content=f"{ERROR} An error occurred. Please try again.",
                view=None
            )
    
    async def _complete_setup(self, interaction: discord.Interaction, state: str, store_id: str, store_info: dict):
        """Complete the setup process with specific store"""
        user_id = interaction.user.id
        username = interaction.user.display_name

        try:
            embed = self.bot.complete_store_setup(
                user_id,
                username,
                state,
                store_info=store_info,
                store_id=store_id
            )
        except StoreSetupError as exc:
            await interaction.response.edit_message(
                content=f"{ERROR} {exc}",
                view=None
            )
            return

        await interaction.response.edit_message(content=None, embed=embed, view=None)

class StoreSearchSelect(discord.ui.Select):
    """Select menu for searching and selecting stores with autocomplete"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str):
        self.bot = bot
        self.state = state
        
        # Get stores for this state
        stores = bot.get_stores_by_state(state)
        
        options = _build_store_options(stores)
        has_options = bool(options)
        if not has_options:
            options = [
                discord.SelectOption(
                    label="No stores available",
                    value="no_stores",
                    description="Try refining your search."
                )
            ]
        super().__init__(
            placeholder="Search and select a store...",
            min_values=1,
            max_values=1,
            options=options
        )

        if not has_options:
            self.disabled = True
    
    async def callback(self, interaction: discord.Interaction):
        """Handle store selection"""
        try:
            selected_store_id = self.values[0]
            if selected_store_id == "no_stores":
                await interaction.response.send_message(
                    f"{ERROR} No stores available. Please try again later.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            selected_store = self.bot.get_store_by_id(selected_store_id)

            if selected_store:
                await self._complete_setup(interaction, self.state, selected_store_id, selected_store)
            else:
                await interaction.response.edit_message(
                    content=f"{ERROR} Store not found. Please try again.",
                    view=None
                )
                
        except Exception as e:
            print(f"Error in store selection: {e}")
            await interaction.response.edit_message(
                content=f"{ERROR} An error occurred. Please try again.",
                view=None
            )
    
    async def _complete_setup(self, interaction: discord.Interaction, state: str, store_id: str, store_info: dict):
        """Complete the setup process with specific store"""
        user_id = interaction.user.id
        username = interaction.user.display_name

        try:
            embed = self.bot.complete_store_setup(
                user_id,
                username,
                state,
                store_info=store_info,
                store_id=store_id
            )
        except StoreSetupError as exc:
            await interaction.response.edit_message(
                content=f"{ERROR} {exc}",
                view=None
            )
            return

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            ephemeral=USE_EPHEMERAL_MESSAGES
        )

class StoreSearchButton(discord.ui.Button):
    """Button to search for stores"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str):
        self.bot = bot
        self.state = state
        
        super().__init__(
            label=f"{SEARCH} Search Stores",
            style=discord.ButtonStyle.secondary,
            emoji=f"{SEARCH}"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Open store search modal"""
        try:
            modal = StoreSearchModal(self.bot, self.state)
            await interaction.response.send_modal(modal)
        except Exception as e:
            print(f"Error opening store search modal: {e}")
            await interaction.response.send_message(
                f"{ERROR} An error occurred. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )

class StoreSearchModal(discord.ui.Modal, title="Search for a Store"):
    """Modal for searching stores by name or ID"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str):
        super().__init__()
        self.bot = bot
        self.state = state
    
    search_query = discord.ui.TextInput(
        label="Store Name or ID",
        placeholder="Enter store name (e.g., 'Bourke St') or ID (e.g., 'W346')",
        required=True,
        min_length=2,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle store search submission"""
        try:
            query = self.search_query.value.strip()
            stores = self.bot.get_stores_by_state(self.state)
            
            # Search by store name or ID
            matching_stores = [
                store for store in stores
                if (
                    query.lower() in store.get('store', '').lower()
                    or query.upper() in store.get('storeId', '').upper()
                )
            ]
            
            if not matching_stores:
                await interaction.response.send_message(
                    f"{ERROR} No stores found matching '{query}' in {STATE_NAMES.get(self.state, self.state)}.\n\n"
                    f"Try searching for a different name or use the browse option.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            # Create store selection view
            if len(matching_stores) == 1:
                # Only one match, complete setup directly
                store = matching_stores[0]
                await self._complete_setup(interaction, self.state, store['storeId'], store)
            else:
                # Multiple matches, show selection
                view = StoreSearchResultsView(self.bot, self.state, matching_stores)
                await interaction.response.send_message(
                    f"{SEARCH} **Store Search Results for '{query}'**\n\n"
                    f"Found {len(matching_stores)} matching stores in {STATE_NAMES.get(self.state, self.state)}:",
                    view=view,
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                
        except Exception as e:
            print(f"Error in store search: {e}")
            await interaction.response.send_message(
                f"{ERROR} An error occurred during search. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
    
    async def _complete_setup(self, interaction: discord.Interaction, state: str, store_id: str, store_info: dict):
        """Complete the setup process with specific store"""
        user_id = interaction.user.id
        username = interaction.user.display_name

        try:
            embed = self.bot.complete_store_setup(
                user_id,
                username,
                state,
                store_info=store_info,
                store_id=store_id
            )
        except StoreSetupError as exc:
            await interaction.response.send_message(
                f"{ERROR} {exc}",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
            return

        await interaction.response.send_message(
            embed=embed,
            ephemeral=USE_EPHEMERAL_MESSAGES
        )

class StoreSearchResultsView(discord.ui.View):
    """View for displaying store search results"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str, stores: list):
        super().__init__(timeout=300)
        self.bot = bot
        self.state = state
        self.stores = stores
        
        # Add store selection dropdown
        self.add_item(StoreSelect(bot, state, stores))
        
        # Add back button
        self.add_item(BackToStoreSelectionButton(bot, state))

class BackToStoreSelectionButton(discord.ui.Button):
    """Button to go back to store selection"""
    
    def __init__(self, bot: 'OfficeworksBot', state: str):
        self.bot = bot
        self.state = state
        
        super().__init__(
            label=f"{BACK_ARROW} Back",
            style=discord.ButtonStyle.secondary,
            emoji=f"{BACK_ICON}"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Go back to store selection"""
        try:
            view = StoreSelectionView(self.bot, self.state)
            await interaction.response.edit_message(
                content=f"{STORE} **Store Setup - {STATE_NAMES.get(self.state, self.state)}**\n\n"
                        f"Please select your preferred store (or choose 'Any store'):",
                view=view
            )
        except Exception as e:
            print(f"Error going back to store selection: {e}")
            await interaction.response.edit_message(
                content=f"{ERROR} An error occurred. Please try again.",
                view=None
            )

class PriceCheckView(discord.ui.View):
    """View with Check Competitors button for price check results"""
    
    def __init__(self, bot: 'OfficeworksBot', product_code: str, product_name: str, 
                 officeworks_price: float, user_id: int):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        self.product_code = product_code
        self.product_name = product_name
        self.officeworks_price = officeworks_price
        self.user_id = user_id
        
        # Add the Check Competitors button
        self.add_item(CheckCompetitorsButton(bot, product_code, product_name, officeworks_price, user_id))

class CheckCompetitorsButton(discord.ui.Button):
    """Button to check competitor prices"""
    
    def __init__(self, bot: 'OfficeworksBot', product_code: str, product_name: str, 
                 officeworks_price: float, user_id: int):
        self.bot = bot
        self.product_code = product_code
        self.product_name = product_name
        self.officeworks_price = officeworks_price
        self.user_id = user_id
        
        super().__init__(
            label="Check Competitors",
            style=discord.ButtonStyle.secondary,
            emoji=f"{COMPARE}"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle competitor price check"""
        try:
            # Ensure only the original user can use the button
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    f"{ERROR} Only the original user can check competitors for this product.",
                    ephemeral=True
                )
                return
            
            await interaction.response.defer(ephemeral=USE_EPHEMERAL_MESSAGES)
            
            # Send status message
            status_msg = await interaction.followup.send(
                f"{PROCESSING} Checking competitor prices for **{self.product_name}**...\n"
                f"Officeworks price: ${self.officeworks_price:.2f}",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
            
            try:
                # Perform price comparison
                comparisons = await price_comparison.search_all_retailers(
                    self.product_name, self.officeworks_price, max_retailers=3
                )
                
                if comparisons:
                    # Create price comparison embed
                    comparison_embed = price_comparison.create_comparison_embed(
                        self.product_name, self.officeworks_price, comparisons
                    )
                    
                    # Add additional context about the original check
                    comparison_embed.add_field(
                        name=f"{STORE_ID} Product Code",
                        value=f"`{self.product_code.upper()}`",
                        inline=True
                    )
                    comparison_embed.add_field(
                        name="Checked",
                        value=get_full_timestamp(datetime.now(timezone.utc)),
                        inline=True
                    )
                    
                    # Edit the status message with results
                    await status_msg.edit(content=None, embed=comparison_embed)
                    
                    # Disable the button to prevent spam
                    self.disabled = True
                    self.label = "✓ Competitors Checked"
                    
                    # Update the original message to disable the button
                    try:
                        await interaction.edit_original_response(view=self.view)
                    except:
                        pass  # If we can't edit the original, that's okay
                        
                else:
                    # No comparison results found
                    no_results_embed = discord.Embed(
                        title=f"{SEARCH} No Competitor Results",
                        description=f"Could not find **{self.product_name}** at other retailers",
                        color=WARNING_COLOR
                    )
                    
                    no_results_embed.add_field(
                        name=f"{STORE} Officeworks Price",
                        value=f"${self.officeworks_price:.2f}",
                        inline=True
                    )
                    no_results_embed.add_field(
                        name=f"{STORE_ID} Product Code",
                        value=f"`{self.product_code.upper()}`",
                        inline=True
                    )
                    
                    no_results_embed.add_field(
                        name="Suggestions",
                        value="• Product may not be available at other retailers\n"
                              "• Try the standalone `/compare` command with different search terms\n"
                              "• Check if the product has alternative names or models",
                        inline=False
                    )
                    
                    await status_msg.edit(content=None, embed=no_results_embed)
                    
                    # Update button
                    self.disabled = True
                    self.label = "No Results Found"
                    self.style = discord.ButtonStyle.danger
                    
                    try:
                        await interaction.edit_original_response(view=self.view)
                    except:
                        pass
                    
            except Exception as e:
                print(f"Error in competitor price check: {e}")
                await status_msg.edit(
                    content=f"{ERROR} Error checking competitor prices: {str(e)}"
                )
                
                # Update button to show error
                self.disabled = True
                self.label = "Check Failed"
                self.style = discord.ButtonStyle.danger
                
                try:
                    await interaction.edit_original_response(view=self.view)
                except:
                    pass
                
        except Exception as e:
            print(f"Error in CheckCompetitorsButton callback: {e}")
            try:
                await interaction.response.send_message(
                    f"{ERROR} An error occurred while checking competitors.",
                    ephemeral=True
                )
            except:
                pass

class OfficeworksBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        # Initialize components
        self.database = Database()
        self.api = OfficeworksAPI()
        self.price_checker = PriceChecker(self, self.database, self.api)
        
        # Configure price comparison with Firecrawl
        price_comparison.firecrawl_client = firecrawl_integration
        
        # Load stores data
        self.stores_data = self._load_stores_data()
        
        # Shutdown flag
        self._shutdown_requested = False

    def _load_stores_data(self):
        """Load stores data from the allstores.md file"""
        try:
            with open('responses/allstores.md', 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse the JSON content
                data = json.loads(content)
                return data
        except Exception as e:
            print(f"Warning: Could not load stores data: {e}")
            return {"states": [], "stores": []}

    def complete_store_setup(self, user_id: int, username: str, state: str,
                              *, store_info: Optional[dict] = None,
                              store_id: Optional[str] = None) -> discord.Embed:
        """Persist the user's store preferences and return a confirmation embed."""

        resolved_store_id = store_id or (store_info.get('storeId') if store_info else None)

        if not self.database.add_user(user_id, username):
            raise StoreSetupError("Failed to create user profile. Please try again.")

        if not self.database.update_user_store(user_id, state, resolved_store_id):
            raise StoreSetupError("Failed to save store preferences. Please try again.")

        return self.create_store_embed(state, store_info)

    def create_store_embed(self, state: str, store_info: Optional[dict]) -> discord.Embed:
        """Generate the confirmation embed for store setup completion."""

        embed = discord.Embed(
            title=f"{SUCCESS} Setup Complete!",
            description="Your Officeworks store preferences have been saved.",
            color=SUCCESS_COLOR
        )

        embed.add_field(name="State", value=STATE_NAMES.get(state, state), inline=True)

        if store_info:
            embed.add_field(name="Store", value=store_info.get('store', 'Unknown Store'), inline=True)

            location_parts = [store_info.get('address', 'N/A')]
            suburb = store_info.get('suburb')
            postcode = store_info.get('postcode')
            suburb_postcode = " ".join(part for part in (suburb, postcode) if part)
            if suburb_postcode:
                location_parts.append(suburb_postcode)
            address_line = ", ".join(part for part in location_parts if part)
            embed.add_field(name="Address", value=address_line, inline=False)

            embed.add_field(name="Phone", value=store_info.get('phone', 'N/A'), inline=True)
            embed.add_field(name="Store ID", value=store_info.get('storeId', 'N/A'), inline=True)
        else:
            state_name = STATE_NAMES.get(state, state)
            embed.add_field(name="Store", value=f"Any store in {state_name}", inline=True)
            embed.add_field(name="Status", value="Ready to track products!", inline=False)

        embed.add_field(
            name="Completed",
            value=get_full_timestamp(datetime.now(timezone.utc)),
            inline=False
        )
        embed.set_footer(text="Use /add to start tracking products")
        return embed

    def get_stores_by_state(self, state: str):
        """Get all stores for a specific state"""
        if not self.stores_data or "stores" not in self.stores_data:
            return []
        
        return [store for store in self.stores_data["stores"] if store["state"] == state]
    
    def get_store_by_id(self, store_id: str):
        """Get a specific store by its ID"""
        if not self.stores_data or "stores" not in self.stores_data:
            return None
        
        return next((store for store in self.stores_data["stores"] if store["storeId"] == store_id), None)

    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        print("Setting up bot...")
        
        # Add cogs
        await self.add_cog(SetupCommands(self))
        await self.add_cog(ProductCommands(self))
        await self.add_cog(UtilityCommands(self))
        
        # Start price checker
        self.price_checker.start()
        
        print("Bot setup complete!")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Bot is ready! Serving {len(self.guilds)} guilds")
        
        # Sync commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
        
        # Start health check task
        asyncio.create_task(self._health_check())
    
    async def _health_check(self):
        """Periodic health check to ensure bot is running properly"""
        while not self._shutdown_requested:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                if self.is_ready():
                    print(f"{SUCCESS} Health check: Bot is healthy at {datetime.now(timezone.utc).strftime('%H:%M:%S')}")
                else:
                    print(f"{WARNING}  Health check: Bot is not ready")
            except Exception as e:
                print(f"{ERROR} Health check error: {e}")
                break
    
    async def on_disconnect(self):
        """Called when the bot disconnects"""
        print("Bot disconnected from Discord")
    
    def request_shutdown(self):
        """Request a graceful shutdown of the bot"""
        self._shutdown_requested = True
        print("Shutdown requested...")
    
    async def close(self):
        """Clean shutdown of the bot"""
        print("Shutting down bot...")
        
        # Stop price checker
        if hasattr(self, 'price_checker') and self.price_checker.is_running:
            self.price_checker.stop()
            print("Price checker stopped")
        
        # Close database connections
        if hasattr(self, 'database'):
            # SQLite connections are automatically closed, but we can add cleanup here if needed
            print("Database connections closed")
        
        await super().close()
        print("Bot shutdown complete")

class SetupCommands(commands.Cog):
    def __init__(self, bot: OfficeworksBot):
        self.bot = bot
    
    @app_commands.command(name="setup", description="Set up your Officeworks store preferences")
    async def setup(self, interaction: discord.Interaction):
        """Set up your preferred Officeworks store location"""
        try:
            # Create state selection view
            view = StateSelectionView(self.bot)
            await interaction.response.send_message(
                f"{STORE} **Officeworks Store Setup**\n\n"
                "Please select your preferred state/territory:",
                view=view,
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
        except Exception as e:
            print(f"Error in setup command: {e}")
            await interaction.response.send_message(
                f"{ERROR} An error occurred during setup. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
    
    @app_commands.command(name="stores", description="List available stores in your state")
    @app_commands.describe(state="Your state (e.g., VIC, NSW, QLD)")
    async def list_stores(self, interaction: discord.Interaction, state: str):
        """List available Officeworks stores in a specific state"""
        try:
            await interaction.response.defer(ephemeral=USE_EPHEMERAL_MESSAGES)
            
            # Validate state
            if state.upper() not in AUSTRALIAN_STATES:
                await interaction.followup.send(
                    f"{ERROR} Invalid state '{state.upper()}'. Please use one of: {', '.join(AUSTRALIAN_STATES)}",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            stores = self.bot.get_stores_by_state(state.upper())
            if not stores:
                await interaction.followup.send(
                    f"{ERROR} No stores found in {state.upper()}.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            # Create embed with store list
            embed = discord.Embed(
                title=f"{STORE} Officeworks Stores in {STATE_NAMES.get(state.upper(), state.upper())}",
                description=f"Found {len(stores)} stores",
                color=INFO_COLOR
            )
            
            # Show first 10 stores (Discord embed limit)
            for i, store in enumerate(stores[:10]):
                store_info = f"**{store['store']}**\n"
                store_info += f"{LOCATION} {store['address']}, {store['suburb']} {store['postcode']}\n"
                store_info += f"{PHONE} {store['phone']}\n"
                store_info += f"{STORE_ID} Store ID: `{store['storeId']}`"
                
                embed.add_field(
                    name=f"{i+1}. {store['store']}",
                    value=store_info,
                    inline=False
                )
            
            if len(stores) > 10:
                embed.add_field(
                    name="Note",
                    value=f"Showing first 10 stores. Total: {len(stores)} stores",
                    inline=False
                )
            
            embed.set_footer(text="Use /setup to configure your preferences")
            
            # Add last updated timestamp
            embed.add_field(
                name="Last Updated",
                value=get_relative_timestamp(datetime.now(timezone.utc)),
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=USE_EPHEMERAL_MESSAGES)
            
        except Exception as e:
            print(f"Error in stores command: {e}")
            await interaction.followup.send(
                f"{ERROR} An error occurred while fetching stores. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
    
    @app_commands.command(name="storestats", description="Show store statistics for all states")
    async def store_stats(self, interaction: discord.Interaction):
        """Show statistics about Officeworks stores across all states"""
        try:
            await interaction.response.defer(ephemeral=USE_EPHEMERAL_MESSAGES)
            
            if not self.bot.stores_data or "stores" not in self.bot.stores_data:
                await interaction.followup.send(
                    f"{ERROR} Store data not available.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            stores = self.bot.stores_data["stores"]
            
            # Count stores by state
            state_counts = {}
            for store in stores:
                state = store['state']
                state_counts[state] = state_counts.get(state, 0) + 1
            
            embed = discord.Embed(
                title=f"{STATISTICS} Officeworks Store Statistics",
                description=f"Total stores: **{len(stores)}**",
                color=INFO_COLOR
            )
            
            # Add state breakdown
            for state in sorted(state_counts.keys()):
                count = state_counts[state]
                state_name = STATE_NAMES.get(state, state)
                embed.add_field(
                    name=f"{state_name} ({state})",
                    value=f"**{count}** stores",
                    inline=True
                )
            
            embed.set_footer(text="Use /stores <state> to see stores in a specific state")
            
            # Add last updated timestamp
            embed.add_field(
                name="Last Updated",
                value=get_relative_timestamp(datetime.now(timezone.utc)),
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=USE_EPHEMERAL_MESSAGES)
            
        except Exception as e:
            print(f"Error in store_stats command: {e}")
            await interaction.followup.send(
                f"{ERROR} An error occurred while fetching store statistics. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )

class ProductCommands(commands.Cog):
    def __init__(self, bot: OfficeworksBot):
        self.bot = bot
    
    @app_commands.command(name="add", description="Add a product to track")
    @app_commands.describe(
        url="Officeworks product URL",
        product_code="Or specify product code directly"
    )
    async def add_product(self, interaction: discord.Interaction, url: str = None, product_code: str = None):
        """Add a product to track for price monitoring"""
        try:
            await interaction.response.defer(ephemeral=USE_EPHEMERAL_MESSAGES)
            
            user_id = interaction.user.id
            
            # Check if user is set up
            user = self.bot.database.get_user(user_id)
            if not user:
                await interaction.followup.send(
                    f"{ERROR} Please set up your store preferences first using `/setup`",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            # Get product code
            if url:
                if not self.bot.api.validate_product_url(url):
                    await interaction.followup.send(
                        f"{ERROR} Invalid Officeworks product URL. Please provide a valid URL.",
                        ephemeral=USE_EPHEMERAL_MESSAGES
                    )
                    return
                
                product_info = self.bot.api.get_product_by_url(url)
                if not product_info:
                    await interaction.followup.send(
                        f"{ERROR} Could not retrieve product information from the URL.",
                        ephemeral=USE_EPHEMERAL_MESSAGES
                    )
                    return
                
                product_code = self.bot.api.extract_product_code(url)
            elif product_code:
                product_info = self.bot.api.get_product_info(product_code)
                if not product_info:
                    await interaction.followup.send(
                        f"{ERROR} Invalid product code. Please check and try again.",
                        ephemeral=USE_EPHEMERAL_MESSAGES
                    )
                    return
            else:
                await interaction.followup.send(
                    f"{ERROR} Please provide either a URL or product code.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            # Check if product is already tracked
            user_products = self.bot.database.get_user_products(user_id)
            if any(p['product_code'].lower() == product_code.lower() for p in user_products):
                await interaction.followup.send(
                    f"{ERROR} Product **{product_code.upper()}** is already being tracked.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            # Add product to database
            if self.bot.database.add_product(
                user_id=user_id,
                product_code=product_code,
                product_name=product_info.get('name'),
                product_url=product_info.get('url'),
                current_price=product_info.get('price')
            ):
                embed = discord.Embed(
                    title=f"{SUCCESS} Product Added!",
                    description=f"**{product_info.get('name', 'Unknown Product')}** has been added to your tracking list.",
                    color=SUCCESS_COLOR
                )
                
                embed.add_field(name="Product Code", value=product_code.upper(), inline=True)
                embed.add_field(name="Current Price", value=f"${product_info.get('price', 0):.2f}", inline=True)
                embed.add_field(name=f"Status", value="{PROCESSING} Monitoring for price drops", inline=True)
                embed.add_field(name="Added", value=get_full_timestamp(datetime.now(timezone.utc)), inline=False)
                
                if product_info.get('image'):
                    embed.set_thumbnail(url=f"https:{product_info['image']}")
                
                embed.set_footer(text="You'll be notified of any price drops!")
                
                await interaction.followup.send(embed=embed, ephemeral=USE_EPHEMERAL_MESSAGES)
            else:
                await interaction.followup.send(
                    f"{ERROR} Failed to add product. Please try again.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                
        except Exception as e:
            print(f"Error in add_product command: {e}")
            await interaction.followup.send(
                f"{ERROR} An error occurred while adding the product. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
    
    @app_commands.command(name="list", description="List your tracked products")
    async def list_products(self, interaction: discord.Interaction):
        """List all products you're currently tracking"""
        try:
            await interaction.response.defer(ephemeral=USE_EPHEMERAL_MESSAGES)
            
            user_id = interaction.user.id
            products = self.bot.database.get_user_products(user_id)
            
            if not products:
                await interaction.followup.send(
                    f"{SORT} You're not tracking any products yet.\n\nUse `/add` to add your first product!",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            embed = discord.Embed(
                title=f"{BROWSE} Your Tracked Products",
                description=f"You're tracking {len(products)} product(s)",
                color=INFO_COLOR
            )
            
            for i, product in enumerate(products, 1):
                product_info = f"**{product['product_name'] or 'Unknown Product'}**\n"
                product_info += f"{STORE_ID} Code: `{product['product_code'].upper()}`\n"
                
                # Handle None values for prices
                current_price = product['current_price'] or 0.0
                lowest_price = product['lowest_price'] or 0.0
                product_info += f"{PRICE} Current: ${current_price:.2f}\n"
                product_info += f"{PRICE_DROP} Lowest: ${lowest_price:.2f}\n"
                
                # Handle None value for last_checked
                if product['last_checked']:
                    product_info += f"{TIME} Last Check: {get_relative_timestamp(product['last_checked'])}"
                else:
                    product_info += f"{TIME} Last Check: Never"
                
                embed.add_field(
                    name=f"{i}. {product['product_code'].upper()}",
                    value=product_info,
                    inline=False
                )
            
            embed.set_footer(text="Use /check to manually check prices")
            
            await interaction.followup.send(embed=embed, ephemeral=USE_EPHEMERAL_MESSAGES)
            
        except Exception as e:
            print(f"Error in list_products command: {e}")
            await interaction.followup.send(
                f"{ERROR} An error occurred while fetching your products. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
    
    @app_commands.command(name="check", description="Manually check the price of a product")
    @app_commands.describe(product_code="Product code to check")
    async def check_price(self, interaction: discord.Interaction, product_code: str):
        """Manually check the current price of a tracked product"""
        try:
            await interaction.response.defer(ephemeral=USE_EPHEMERAL_MESSAGES)
            
            user_id = interaction.user.id
            
            # Check if product is tracked
            user_products = self.bot.database.get_user_products(user_id)
            tracked_product = next((p for p in user_products if p['product_code'].lower() == product_code.lower()), None)
            
            if not tracked_product:
                await interaction.followup.send(
                    f"{ERROR} Product **{product_code.upper()}** is not in your tracking list.\n\nUse `/add` to add it first!",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            # Check price now
            result = await self.bot.price_checker.check_product_now(product_code, user_id)
            
            if result:
                current_price = result.get('new_price') or result.get('current_price', 0)
                product_name = result.get('name', 'Unknown Product')
                
                # Create main price check embed
                if result['updated']:
                    embed = discord.Embed(
                        title=f"{PRICE} Price Check Complete",
                        description=f"**{product_name}** price has been updated!",
                        color=SUCCESS_COLOR
                    )
                    
                    embed.add_field(name="Product Code", value=product_code.upper(), inline=True)
                    embed.add_field(name="Old Price", value=f"${result['old_price']:.2f}", inline=True)
                    embed.add_field(name="New Price", value=f"${result['new_price']:.2f}", inline=True)
                    
                    if result['price_drop'] > 0:
                        embed.add_field(
                            name="🎉 Price Drop!",
                            value=f"You saved ${result['price_drop']:.2f}!",
                            inline=False
                        )
                        embed.color = 0x00ff00
                    else:
                        embed.add_field(
                            name=f"{STATISTICS} Price Status",
                            value="Price unchanged or increased",
                            inline=False
                        )
                        embed.color = 0xffff00
                else:
                    # Product is tracked but no price change occurred
                    embed = discord.Embed(
                        title=f"{PRICE} Price Check Complete",
                        description=f"**{product_name}** current price:",
                        color=INFO_COLOR
                    )
                    
                    embed.add_field(name="Product Code", value=product_code.upper(), inline=True)
                    embed.add_field(name="Current Price", value=f"${current_price:.2f}", inline=True)
                    embed.add_field(name="Status", value="Price unchanged", inline=True)
                
                embed.add_field(name="Checked", value=get_full_timestamp(datetime.now(timezone.utc)), inline=False)
                
                # Create a view with the "Check Competitors" button
                view = PriceCheckView(self.bot, product_code, product_name, current_price, user_id)
                
                # Send initial price check result with the button
                await interaction.followup.send(embed=embed, view=view, ephemeral=USE_EPHEMERAL_MESSAGES)
                    
            else:
                await interaction.followup.send(
                    f"{ERROR} Could not check price for **{product_code.upper()}**. Please try again.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                
        except Exception as e:
            print(f"Error in check_price command: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(
                f"{ERROR} An error occurred while checking the price: {str(e)}. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
    
    @app_commands.command(name="remove", description="Remove a product from tracking")
    @app_commands.describe(product_code="Product code to remove")
    async def remove_product(self, interaction: discord.Interaction, product_code: str):
        """Remove a product from your tracking list"""
        try:
            user_id = interaction.user.id
            
            # Check if product is tracked
            user_products = self.bot.database.get_user_products(user_id)
            tracked_product = next((p for p in user_products if p['product_code'].lower() == product_code.lower()), None)
            
            if not tracked_product:
                await interaction.response.send_message(
                    f"{ERROR} Product **{product_code.upper()}** is not in your tracking list.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                return
            
            # Remove product
            if self.bot.database.remove_product(user_id, product_code):
                embed = discord.Embed(
                    title=f"{SUCCESS} Product Removed",
                    description=f"**{tracked_product['product_name'] or 'Unknown Product'}** has been removed from tracking.",
                    color=ERROR_COLOR,
                    timestamp=datetime.now(timezone.utc)
                )
                
                embed.add_field(name="Product Code", value=product_code.upper(), inline=True)
                embed.add_field(name=f"Status", value="{ERROR} No longer monitoring", inline=True)
                
                embed.set_footer(text="Use /add to track it again anytime")
                
                await interaction.response.send_message(embed=embed, ephemeral=USE_EPHEMERAL_MESSAGES)
            else:
                await interaction.response.send_message(
                    f"{ERROR} Failed to remove product. Please try again.",
                    ephemeral=USE_EPHEMERAL_MESSAGES
                )
                
        except Exception as e:
            print(f"Error in remove_product command: {e}")
            await interaction.response.send_message(
                f"{ERROR} An error occurred while removing the product. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
    
    @app_commands.command(name="compare", description="Compare prices across multiple retailers")
    @app_commands.describe(
        search_query="Product name or description to search for across retailers",
        officeworks_price="Optional: Officeworks price for comparison (if known)"
    )
    async def compare_prices(self, interaction: discord.Interaction, search_query: str, officeworks_price: float = None):
        """Compare prices across multiple retailers for any product"""
        try:
            await interaction.response.defer(ephemeral=USE_EPHEMERAL_MESSAGES)
            
            # If no Officeworks price provided, try to get it from the API
            if officeworks_price is None:
                try:
                    # Try to extract product code from search query if it looks like one
                    potential_code = search_query.strip().lower()
                    if len(potential_code) <= 15 and not ' ' in potential_code:
                        product_info = self.bot.api.get_product_info(potential_code)
                        if product_info and product_info.get('price'):
                            officeworks_price = product_info['price']
                            search_query = product_info.get('name', search_query)
                except Exception:
                    pass  # Continue with manual search
            
            # Default price for comparison if none provided
            if officeworks_price is None:
                officeworks_price = 999999.99  # High default so other retailers show as cheaper
                price_note = "No Officeworks price provided - showing all found prices"
            else:
                price_note = f"Comparing against Officeworks price: ${officeworks_price:.2f}"
            
            # Send initial status message
            status_msg = await interaction.followup.send(
                f"{PROCESSING} Searching retailers for **{search_query}**...\n{price_note}",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
            
            # Perform price comparison across retailers
            comparisons = await price_comparison.search_all_retailers(
                search_query, officeworks_price, max_retailers=3
            )
            
            if comparisons:
                # Create price comparison embed
                comparison_embed = price_comparison.create_comparison_embed(
                    search_query, officeworks_price, comparisons
                )
                
                # If no officeworks price was provided, update the embed
                if officeworks_price == 999999.99:
                    comparison_embed.title = f"{COMPARE} Retailer Price Search Results"
                    comparison_embed.description = f"Found prices for **{search_query}** across retailers"
                    # Remove the Officeworks field since we don't have a real price
                    if comparison_embed.fields and comparison_embed.fields[0].name.startswith(f"{STORE}"):
                        comparison_embed.remove_field(0)
                
                # Edit the status message with results
                await status_msg.edit(content=None, embed=comparison_embed)
                
            else:
                # No results found
                no_results_embed = discord.Embed(
                    title=f"{SEARCH} No Results Found",
                    description=f"Could not find **{search_query}** at other retailers",
                    color=WARNING_COLOR
                )
                
                no_results_embed.add_field(
                    name="Suggestions",
                    value="• Try a shorter or more generic search term\n"
                          "• Check the spelling\n" 
                          "• Try searching for the brand or model number",
                    inline=False
                )
                
                no_results_embed.add_field(
                    name="Search Query",
                    value=f"`{search_query}`",
                    inline=True
                )
                
                if officeworks_price != 999999.99:
                    no_results_embed.add_field(
                        name="Officeworks Price",
                        value=f"${officeworks_price:.2f}",
                        inline=True
                    )
                
                await status_msg.edit(content=None, embed=no_results_embed)
                
        except Exception as e:
            print(f"Error in compare_prices command: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(
                f"{ERROR} An error occurred during price comparison: {str(e)}",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )

class UtilityCommands(commands.Cog):
    def __init__(self, bot: OfficeworksBot):
        self.bot = bot
    
    @app_commands.command(name="status", description="Check bot and price monitoring status")
    async def status(self, interaction: discord.Interaction):
        """Check the current status of the bot and price monitoring"""
        try:
            await interaction.response.defer(ephemeral=USE_EPHEMERAL_MESSAGES)
            
            user_id = interaction.user.id
            user = self.bot.database.get_user(user_id)
            user_products = self.bot.database.get_user_products(user_id)
            
            embed = discord.Embed(
                title=f"{BOT} Bot Status",
                description="Officeworks Price Tracker Status",
                color=INFO_COLOR
            )
            
            # Bot status
            embed.add_field(
                name="Bot Status",
                value=f"{ONLINE} Online" if self.bot.is_ready() else "{OFFLINE} Offline",
                inline=True
            )
            
            # Price checker status
            embed.add_field(
                name="Price Monitoring",
                value=f"{ONLINE} Active" if self.bot.price_checker.is_running else "{OFFLINE} Inactive",
                inline=True
            )
            
            # Next check time
            next_check = self.bot.price_checker.get_next_check_time()
            if next_check:
                embed.add_field(
                    name="Next Price Check",
                    value=get_future_relative_time(next_check),
                    inline=True
                )
            
            # User status
            if user:
                embed.add_field(
                    name="Your Store",
                    value=user.get('preferred_state', 'Not set'),
                    inline=True
                )
                embed.add_field(
                    name="Tracked Products",
                    value=len(user_products),
                    inline=True
                )
                
                if user.get('preferred_store_id'):
                    embed.add_field(
                        name="Store ID",
                        value=user['preferred_store_id'],
                        inline=True
                    )
            else:
                embed.add_field(
                    name="Your Status",
                    value=f"{ERROR} Not set up",
                    inline=True
                )
            
            embed.set_footer(text="Use /setup to configure your preferences")
            
            # Add last updated timestamp
            embed.add_field(
                name="Last Updated",
                value=get_relative_timestamp(datetime.now(timezone.utc)),
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=USE_EPHEMERAL_MESSAGES)
            
        except Exception as e:
            print(f"Error in status command: {e}")
            await interaction.followup.send(
                f"{ERROR} An error occurred while checking status. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )
    
    @app_commands.command(name="help", description="Show help information")
    async def help_command(self, interaction: discord.Interaction):
        """Show help information for all commands"""
        try:
            embed = discord.Embed(
                title=f"{HELP} Officeworks Price Tracker Help",
                description="Track Officeworks product prices and get notified of drops!",
                color=INFO_COLOR
            )
            
            # Setup commands
            embed.add_field(
                name=f"{FILTER} Setup Commands",
                value="`/setup` - Set your preferred store location\n"
                      "`/stores` - List available stores in a state\n"
                      "`/storestats` - Show store statistics across all states",
                inline=False
            )
            
            # Product commands
            embed.add_field(
                name=f"{PRODUCT} Product Commands",
                value="`/add` - Add a product to track\n"
                      "`/list` - List your tracked products\n"
                      "`/check` - Check product price (with 'Check Competitors' button)\n"
                      "`/remove` - Remove a product from tracking\n"
                      "`/compare` - Compare prices across retailers",
                inline=False
            )
            
            # Utility commands
            embed.add_field(
                name=f"{TOOLS} Utility Commands",
                value="`/status` - Check bot status\n"
                      "`/help` - Show this help message",
                inline=False
            )
            
            # How to use
            embed.add_field(
                name=f"{GETTING_STARTED} Getting Started",
                value="1. Use `/setup` to set your store location\n"
                      "2. Use `/add` with an Officeworks product URL\n"
                      "3. The bot will automatically monitor prices\n"
                      "4. Get notified of price drops via DM!",
                inline=False
            )
            
            # Examples
            embed.add_field(
                name=f"{TIP} Examples",
                value="`/add url:https://www.officeworks.com.au/shop/officeworks/p/ipad-mini-a17-pro-8-3-wifi-128gb-space-grey-ipdmw128g`\n"
                      "`/check product_code:ipdmw128g` (then click 'Check Competitors' button)\n"
                      "`/compare search_query:iPad Mini 128GB`",
                inline=False
            )
            
            embed.set_footer(text="Prices are checked every 30 minutes automatically")
            
            await interaction.response.send_message(embed=embed, ephemeral=USE_EPHEMERAL_MESSAGES)
            
        except Exception as e:
            print(f"Error in help command: {e}")
            await interaction.response.send_message(
                f"{ERROR} An error occurred while showing help. Please try again.",
                ephemeral=USE_EPHEMERAL_MESSAGES
            )

class SignalHandler:
    """Handle system signals for graceful shutdown"""
    def __init__(self, bot: OfficeworksBot):
        self.bot = bot
        self.loop = asyncio.get_event_loop()
        
        # Register signal handlers
        if sys.platform != 'win32':
            # Unix-like systems
            self.loop.add_signal_handler(signal.SIGINT, self._signal_handler)
            self.loop.add_signal_handler(signal.SIGTERM, self._signal_handler)
        else:
            # Windows
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum=None, frame=None):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum or 'SIGINT/SIGTERM'}")
        print("Gracefully shutting down...")
        
        # Schedule shutdown in the event loop
        asyncio.create_task(self._shutdown())
    
    async def _shutdown(self):
        """Perform graceful shutdown"""
        try:
            await self.bot.close()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            self.loop.stop()

async def main():
    """Main function to run the bot"""
    bot = OfficeworksBot()
    
    try:
        print("Starting Officeworks Price Tracker Bot...")
        print("Press Ctrl+C to stop the bot gracefully")
        
        # Set up signal handling
        signal_handler = SignalHandler(bot)
        
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal (Ctrl+C)")
        print("Gracefully shutting down...")
    except Exception as e:
        print(f"{ERROR} Error running bot: {e}")
    finally:
        try:
            await bot.close()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        print("Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
