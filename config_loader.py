import configparser  # ✅ Ensure configparser is imported
from solana.rpc.api import Client

def load_config():
    """Loads configuration settings from config.ini"""
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config

# Load configuration
config = load_config()

# Validate RPC URL
RPC_URL = config.get("solanaConfig", "main_url", fallback=None)
if not RPC_URL:
    raise ValueError("❌ Solana RPC URL is missing in config.ini. Please check your configuration.")

# Initialize Solana client
solana_client = Client(RPC_URL)
print(f"✅ Solana RPC Client initialized with URL: {RPC_URL}")

