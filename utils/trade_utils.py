from solana.transaction import Transaction
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.instructions import transfer, get_associated_token_address
from config_loader import solana_client
from logger import logger

def buy(pool_address: str, payer: Keypair, sol_amount: float):
    try:
        transaction = Transaction()
        transaction.add(
            transfer(
                source=Pubkey(pool_address),
                dest=get_associated_token_address(payer.public_key, Pubkey(pool_address)),
                owner=payer.public_key,
                amount=int(sol_amount * 10**9)
            )
        )
        result = solana_client.send_transaction(transaction, payer)
        logger.info(f"Buy order executed: {result}")
        return result
    except Exception as e:
        logger.error(f"Buy order failed: {e}")

def sell(pool_address: str, payer: Keypair, sol_amount: float):
    try:
        transaction = Transaction()
        transaction.add(
            transfer(
                source=get_associated_token_address(payer.public_key, Pubkey(pool_address)),
                dest=Pubkey(pool_address),
                owner=payer.public_key,
                amount=int(sol_amount * 10**9)
            )
        )
        result = solana_client.send_transaction(transaction, payer)
        logger.info(f"Sell order executed: {result}")
        return result
    except Exception as e:
        logger.error(f"Sell order failed: {e}")