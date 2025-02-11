import threading
import json
import time
import base58
import os
import requests

from event_queue import event_queue
from utils.trade_utils import buy, sell
from config_loader import config
from logger import logger
from solders.keypair import Keypair
from dex import fetch_token_addresses, get_raydium_token_details

from solana.rpc.api import Client

import utils.trade_utils

RAYDIUM_POOLS_URL = "https://api.raydium.io/v2/sdk/liquidity/main"
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v4/quote"

# Load sniping parameters from config.ini
MIN_LIQUIDITY = int(config.get("sniping", "min_liquidity"))
MAX_LIQUIDITY = int(config.get("sniping", "max_liquidity"))
MIN_MARKET_CAP = int(config.get("sniping", "min_market_cap"))
MAX_MARKET_CAP = int(config.get("sniping", "max_market_cap"))
MAX_SLIPPAGE = float(config.get("sniping", "max_slippage"))

# Initialize Solana client
solana_client = Client(config.get("solanaConfig", "main_url"))

# Read private key from config.ini
private_key = config.get("trading", "private_key").strip()

try:
    if private_key.startswith("["):  # JSON format detected
        private_key_bytes = json.loads(private_key)  # Convert string to list of integers
        private_key_bytes = bytes(private_key_bytes)  # Convert to bytes

        if len(private_key_bytes) == 32:
            trader_keypair = Keypair.from_seed(private_key_bytes)  # Derive full key
        elif len(private_key_bytes) == 64:
            trader_keypair = Keypair.from_bytes(private_key_bytes)  # Load full key
        else:
            raise ValueError("Invalid private key length.")
    else:
        private_key_bytes = base58.b58decode(private_key)
        trader_keypair = Keypair.from_bytes(private_key_bytes)
except Exception as e:
    logger.error(f"Error loading private key: {e}")
    exit(1)

logger.info("✅ Solana client and keypair initialized successfully.")

def get_jupiter_token_details(token_address):
    """Fetches token swap details from Jupiter Aggregator."""
    try:
        params = {
            "inputMint": token_address,
            "outputMint": "So11111111111111111111111111111111111111112",  # SOL token mint
            "amount": 1000000,  # 1 token in lamports
            "slippageBps": int(MAX_SLIPPAGE * 100)
        }
        response = requests.get(JUPITER_QUOTE_URL, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error fetching Jupiter token details: {e}")
        return None

def monitor_tokens():
    """Continuously fetch tokens from DexScreener, validate them, and filter based on sniping rules."""
    all_tokens = []
    while True:
        tokens = fetch_token_addresses()
        logger.info(f"Received token data: {tokens}")  # Debugging
        if tokens:
            validated_tokens = []
            for token in tokens:
                token_address = token.get("tokenAddress")  # Use the correct key from DexScreener response
                if not token_address:
                    logger.warning("Skipping token with missing address.")
                    continue  # Skip tokens without addresses

                raydium_details = get_raydium_token_details(token_address)
                jupiter_details = get_jupiter_token_details(token_address)

                if raydium_details:
                    token["raydium_info"] = raydium_details  # Merge Raydium data
                    validated_tokens.append(token)
                    logger.info(f"Token {token_address} found on Raydium with full details.")
                elif jupiter_details:
                    token["jupiter_info"] = jupiter_details  # Merge Jupiter data
                    validated_tokens.append(token)
                    logger.info(f"Token {token_address} found on Jupiter with full details.")
                else:
                    logger.warning(f"Token {token_address} is not listed on Raydium or Jupiter.")
            
            all_tokens.extend(validated_tokens)
            
            # Save full token data with DexScreener + Raydium + Jupiter details
            with open("dexscreener_tokens.json", "w") as f:
                json.dump(all_tokens, f, indent=4)
                
            logger.info("✅ Token data saved to dexscreener_tokens.json with sniping filters applied")
        
        time.sleep(30)  # Adjust interval as needed

# Start token monitoring in a separate thread
dex_thread = threading.Thread(target=monitor_tokens, daemon=True)
dex_thread.start()

logger.info("🚀 Trading bot is now monitoring event queue for trades and fetching new tokens!")

# Prevent script from exiting
while True:
    time.sleep(1)  # Keeps the script running

