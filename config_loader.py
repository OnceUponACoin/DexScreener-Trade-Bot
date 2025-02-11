import configparser
from solana.rpc.api import Client

def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config

config = load_config()
solana_client = Client(config.get("solanaConfig", "main_url"))