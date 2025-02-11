import json
import requests
import threading
import time
from config_loader import config, solana_client
from event_queue import event_queue
from logger import logger

# ✅ Fixed Solana import issues
try:
    from solders.pubkey import Pubkey as PublicKey
except ImportError:
    raise ImportError("No compatible PublicKey module found. Try `pip install solders`")

from solana.rpc.api import Client
from spl.token.instructions import get_associated_token_address


DEX_API_URL = "https://api.dexscreener.com/token-profiles/latest/v1"
RAYDIUM_POOLS_URL = "https://api.raydium.io/v2/sdk/liquidity/main"
TRADE_HISTORY = {}  # Stores entry prices for active trades

# Load sniping conditions from config.ini
MIN_LIQUIDITY = int(config.get("sniping", "min_liquidity"))
MAX_LIQUIDITY = int(config.get("sniping", "max_liquidity"))
MIN_MARKET_CAP = int(config.get("sniping", "min_market_cap"))
MAX_MARKET_CAP = int(config.get("sniping", "max_market_cap"))
MIN_PRICE_CHANGE = float(config.get("sniping", "min_price_change"))  # Percentage

def get_onchain_token_info(token_address):
    """Fetch on-chain token metadata"""
    try:
        token_pubkey = PublicKey(token_address)
        associated_token_address = get_associated_token_address(token_pubkey, solana_client.get_account_info(token_pubkey))
        return associated_token_address
    except Exception as e:
        logger.error(f"Failed to fetch on-chain token info: {e}")
        return None

def is_token_on_raydium(token_address):
    """Check if the token is available for trading on Raydium"""
    try:
        response = requests.get(RAYDIUM_POOLS_URL)
        if response.status_code == 200:
            pools = response.json()
            for pool in pools:
                if token_address in [pool["baseMint"], pool["quoteMint"]]:
                    return True  # Token is tradable on Raydium
        return False
    except Exception as e:
        logger.error(f"Error fetching Raydium pools: {e}")
        return False

def process_token_from_dexscreener(token_info):
    """Process and validate token before adding to event queue"""
    token_address = token_info.get("token_address")
    liquidity = token_info.get("liquidity", 0)
    market_cap = token_info.get("market_cap", 0)
    price_change = token_info.get("price_change", 0)
    
    if not token_address:
        logger.warning("Token address missing in fetched data.")
        return
    
    # Apply filters
    if not (MIN_LIQUIDITY <= liquidity <= MAX_LIQUIDITY):
        return
    if not (MIN_MARKET_CAP <= market_cap <= MAX_MARKET_CAP):
        return
    if price_change < MIN_PRICE_CHANGE:
        return
    
    # Validate on Raydium
    if not is_token_on_raydium(token_address):
        logger.warning(f"Token {token_address} is NOT available on Raydium.")
        return
    
    # Add to event queue for trading
    event_queue.put(token_info)
    logger.info(f"Token {token_address} added to trading queue.")

def fetch_token_addresses():
    """Fetch new tokens from DexScreener and validate them"""
    try:
        response = requests.get(DEX_API_URL)
        data = response.json()
        
        if isinstance(data, list):  # Handle case where API returns a list
            token_list = data
        elif isinstance(data, dict) and "tokens" in data:  # Handle expected dictionary format
            token_list = data["tokens"]
        else:
            logger.error("Unexpected API response format from DexScreener.")
            return []
        
        return token_list

    except Exception as e:
        logger.error(f"Error fetching token addresses: {e}")
        return []

def get_raydium_token_details(token_address):
    """Fetches token details from Raydium's liquidity pools."""
    try:
        response = requests.get(RAYDIUM_POOLS_URL)
        if response.status_code == 200:
            pools = response.json()
            for pool in pools:
                if token_address in [pool["baseMint"], pool["quoteMint"]]:
                    return pool  # Return full pool details
        return None
    except Exception as e:
        logger.error(f"Error fetching Raydium token details: {e}")
        return None



def start_token_monitoring(interval=30):
    """Continuously fetch and validate tokens at regular intervals"""
    while True:
        fetch_token_addresses()
        time.sleep(interval)

# Run monitoring in a separate thread
monitoring_thread = threading.Thread(target=start_token_monitoring, daemon=True)
monitoring_thread.start()

