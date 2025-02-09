import json
import logging
import requests
import time
import configparser
from datetime import datetime, timedelta
import threading

# Configure Logging
logging.basicConfig(
    filename="dexscraper.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")

DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/search?q=solana"

# Load filtering parameters
min_liquidity = int(config["sniping"]["min_liquidity"])
max_liquidity = int(config["sniping"]["max_liquidity"])
min_market_cap = int(config["sniping"]["min_market_cap"])
max_market_cap = int(config["sniping"]["max_market_cap"])
min_price_change = float(config["sniping"]["min_price_change"])
min_token_age = int(config["sniping"]["min_token_age"])
min_buy_volume = int(config["sniping"]["min_buy_volume"])
min_sell_volume = int(config["sniping"]["min_sell_volume"])
interval_seconds = 5

def fetch_dex_pools():
    """Fetches new liquidity pools from DexScreener HTTP API"""
    logging.info("🔄 Fetching new pools from DexScreener...")
    response = requests.get(DEXSCREENER_API_URL)
    if response.status_code != 200:
        logging.error("❌ Failed to fetch data from DexScreener API")
        return []
    
    data = response.json()
    return data.get("pairs", [])

def filter_pools(pools):
    """Filters liquidity pools based on defined criteria."""
    filtered_pools = []
    now = datetime.utcnow()
    
    for pool in pools:
        liquidity = pool.get("liquidity", {}).get("usd", 0)
        market_cap = pool.get("marketCap", 0)
        price_change = pool.get("priceChange", {}).get("h24", 0)
        created_at_str = pool.get("createdAt", now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        try:
            created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            created_at = now  # Default to now if parsing fails
        
        token_age = (now - created_at).total_seconds() / 3600  # Convert seconds to hours
        buy_volume = pool.get("volume", {}).get("buy", 0)
        sell_volume = pool.get("volume", {}).get("sell", 0)
        
        if not (min_liquidity <= liquidity <= max_liquidity):
            logging.info(f"❌ Rejected {pool['pairAddress']} due to liquidity: {liquidity}")
            continue
        
        if not (min_market_cap <= market_cap <= max_market_cap):
            logging.info(f"❌ Rejected {pool['pairAddress']} due to market cap: {market_cap}")
            continue
        
        if price_change < min_price_change:
            logging.info(f"❌ Rejected {pool['pairAddress']} due to price change: {price_change}%")
            continue
        
        if token_age < min_token_age:
            logging.info(f"❌ Rejected {pool['pairAddress']} due to token age: {token_age} hours")
            continue
        
        if buy_volume < min_buy_volume or sell_volume < min_sell_volume:
            logging.info(f"❌ Rejected {pool['pairAddress']} due to volume - Buy: {buy_volume}, Sell: {sell_volume}")
            continue
        
        filtered_pools.append(pool)
    
    return filtered_pools

def start_dexscraper():
    """Starts the DEX scraper to fetch and filter pools at intervals."""
    while True:
        pools = fetch_dex_pools()
        filtered_pools = filter_pools(pools)
        
        for pool in filtered_pools:
            logging.info(f"✅ Approved: {pool['pairAddress']} | Liquidity: {pool['liquidity']['usd']} | Market Cap: {pool['marketCap']}")
            
            # Send this pool for further processing (buy/sell decision)
            from main import handle_new_pool
            handle_new_pool(pool)
        
        logging.info(f"⏳ Waiting {interval_seconds} seconds before next update...")
        time.sleep(interval_seconds)

def main():
    dex_thread = threading.Thread(target=start_dexscraper, daemon=True)
    dex_thread.start()
    while True:
        time.sleep(1)  # Keep the main thread alive

if __name__ == "__main__":
    main()
