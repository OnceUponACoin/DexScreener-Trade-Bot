from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.instructions import transfer, get_associated_token_address
from solders.instruction import Instruction as TransactionInstruction
from config_loader import solana_client, config
from logger import logger
import os
import json
import base58
import sys
import requests

RAYDIUM_SWAP_PROGRAM_ID = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")
TRADE_HISTORY = {}  # Stores entry prices for active trades

# Prevent multiple instances using a lock file
LOCK_FILE = "/tmp/trade_script.lock"
if os.path.exists(LOCK_FILE):
    logger.error("🚨 Another instance is already running. Exiting...")
    sys.exit(1)
else:
    open(LOCK_FILE, 'w').close()

# Ensure lock file is removed on exit
import atexit
atexit.register(lambda: os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None)

# Load private key from config.ini
private_key = config.get("trading", "private_key").strip()
if private_key.startswith("["):
    private_key_bytes = bytes(json.loads(private_key))
elif len(base58.b58decode(private_key)) in [32, 64]:
    private_key_bytes = base58.b58decode(private_key)
else:
    logger.error("Invalid private key format.")
    sys.exit(1)

trader_keypair = Keypair.from_bytes(private_key_bytes)

def create_raydium_swap_instruction(token_address, amount, trade_type):
    """Creates a transaction instruction to interact with Raydium's AMM pools"""
    try:
        instruction_data = {
            "tradeType": trade_type,
            "amount": amount,
            "tokenAddress": token_address,
        }
        return TransactionInstruction(
            program_id=RAYDIUM_SWAP_PROGRAM_ID,
            keys=[
                {"pubkey": trader_keypair.pubkey(), "is_signer": True, "is_writable": True},
                {"pubkey": Pubkey.from_string(token_address), "is_signer": False, "is_writable": True},
            ],
            data=json.dumps(instruction_data).encode()
        )
    except Exception as e:
        logger.error(f"Error creating Raydium swap instruction: {e}")
        return None

def execute_trade_on_raydium(token_address, amount, trade_type="buy"):
    """Executes a trade on Raydium's AMM pools using Solana transactions"""
    try:
        instruction = create_raydium_swap_instruction(token_address, amount, trade_type)
        if not instruction:
            return None
        
        transaction = Transaction()
        transaction.add(instruction)
        
        result = solana_client.send_transaction(transaction, trader_keypair)
        if result["result"]:
            logger.info(f"✅ Trade successful: {result}")
            return result
        else:
            logger.error(f"❌ Trade failed: {result}")
            return None
    except Exception as e:
        logger.error(f"❌ Trade execution error: {e}")
        return None

def buy(token_address, amount):
    """Buys a token on Raydium via AMM pools"""
    logger.info(f"Attempting to buy {amount} of {token_address} on Raydium")
    return execute_trade_on_raydium(token_address, amount, trade_type="buy")

def sell(token_address, amount):
    """Sells a token on Raydium via AMM pools"""
    logger.info(f"Attempting to sell {amount} of {token_address} on Raydium")
    return execute_trade_on_raydium(token_address, amount, trade_type="sell")

