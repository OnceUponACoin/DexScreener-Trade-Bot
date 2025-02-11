import json
import time
import threading
import requests
from datetime import datetime
from config_loader import config
from event_queue import event_queue
from logger import logger

DEX_API_URL = "https://api.dexscreener.com/token-profiles/latest/v1"

def fetch_token_data():
    try:
        response = requests.get(DEX_API_URL)
        if response.status_code == 200:
            data = response.json()
            return data
    except Exception as e:
        logger.error(f"Error fetching data from DEX: {e}")
    return None

def start_token_monitoring():
    while True:
        token_data = fetch_token_data()
        if token_data:
            for token in token_data.get("tokens", []):
                price = token.get("price")
                liquidity = token.get("liquidity")
                action = "BUY" if price > 2 else "SELL"
                event_queue.put({"token": token["symbol"], "price": price, "action": action})
                logger.info(f"Added event: {token['symbol']} {action} at {price}")
        time.sleep(10)

monitoring_thread = threading.Thread(target=start_token_monitoring, daemon=True)
monitoring_thread.start()