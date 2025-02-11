import threading
from event_queue import event_queue
from utils.trade_utils import buy, sell
from config_loader import config
from logger import logger
from solders.keypair import Keypair

private_key = config.get("trading", "private_key")
trader_keypair = Keypair.from_base58_string(private_key)

def process_events():
    while True:
        event = event_queue.get()
        if event:
            logger.info(f"Processing event: {event}")
            if event["action"] == "BUY":
                buy(event["token"], trader_keypair, float(config.get("trading", "sol_amount")))
            elif event["action"] == "SELL":
                sell(event["token"], trader_keypair, float(config.get("trading", "sol_amount")))

event_processor_thread = threading.Thread(target=process_events, daemon=True)
event_processor_thread.start()