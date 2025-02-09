import configparser
import json
import os
import base58
import logging
import requests
import threading
from solana.rpc.api import Client
from solders.keypair import Keypair
from dex import start_dexscraper  # Import DexScreener function

# Clear any existing handlers to prevent duplicates
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure Logging
logging.basicConfig(
    filename="bot.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"  # Overwrite the log file on each run
)

# Also log to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)

logging.info("🔹 Bot started and logging initialized.")

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Telegram Bot Configuration
TELEGRAM_TOKEN = config.get("telegram", "telegram_token", fallback="")
TELEGRAM_CHAT_ID = config.get("telegram", "telegram_chat_id", fallback="")

# RPC Configuration
rpc_url = config["solanaConfig"]["main_url"]
solana_client = Client(rpc_url)

# Trading Configuration
private_key_string = config["trading"]["private_key"]
private_key_bytes = base58.b58decode(private_key_string)
if len(private_key_bytes) == 32:
    payer = Keypair.from_seed(private_key_bytes)  # Correctly derives the full key
else:
    payer = Keypair.from_bytes(private_key_bytes)  # Already 64 bytes
sol_amount = float(config.get("trading", "sol_amount", fallback="0.5"))

def send_telegram_message(message):
    """Send a message to Telegram and log errors."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        logging.debug(f"📩 Telegram response: {response_data}")
        if not response_data.get("ok"):
            logging.error(f"❌ Telegram Error: {response_data}")
    except Exception as e:
        logging.error(f"❌ Failed to send Telegram message: {e}")

def handle_new_pool(pool_address, base_token, liquidity):
    """Handles new pools detected by DexScreener."""
    logging.info(f"🔍 Checking new pool: {pool_address} - Liquidity: ${liquidity}")

    if liquidity < 10_000:
        logging.warning(f"⚠️ Skipping {pool_address} - Low Liquidity (${liquidity})")
        return

    logging.info(f"💰 Sniping {pool_address} - Liquidity: ${liquidity}")

    # Execute buy function
    from utils.trade_utils import buy
    buy(solana_client, pool_address, payer, sol_amount, {})

# Start Dexscraper WebSocket
threading.Thread(target=start_dexscraper, daemon=True).start()

if __name__ == "__main__":
    logging.info("🚀 Sniper bot is starting...")
    print("🚀 Sniper bot is starting...")
    start_dexscraper()  # Ensure Dexscraper starts

