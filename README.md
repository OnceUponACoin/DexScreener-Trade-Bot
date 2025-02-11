# DexScreener Sniping Bot

## **Donations**
Making scripts and other useful tools takes time and energy. A little help goes a long way. If you do donate, know it will go towards bigger and better things.

ETH: 0x0eF640DD0059E793D7121dB21B5158D2CCbD1e24

##Update

This is the final version. The bot does not have access to the trades DEX the DexScreener uses. If found, I will incorporate it later.

## Overview

This bot is designed to snipe newly listed tokens on Solana by fetching data from **DexScreener**, verifying tokens on **Raydium** and **Jupiter**, and executing trades based on pre-configured sniping parameters.

## Features

- Fetches new tokens from **DexScreener**.
- Validates tokens on **Raydium** and **Jupiter**.
- Filters tokens based on market cap, liquidity, and slippage settings.
- Executes trades automatically if a token meets the sniping criteria.
- Multi-threaded for continuous token monitoring and trade execution.
- Fully configurable through a `config.ini` file.

## Installation

### Prerequisites

Ensure you have **Python 3.8+** installed along with the following dependencies:

```sh
pip install -r requirements.txt
```

### Configuration

1. Copy `config.ini.example` to `config.ini`.
2. Edit the `config.ini` file with your Solana private key and preferred sniping parameters.

Example configuration:

```ini
[solanaConfig]
main_url = https://api.devnet.solana.com

[trading]
private_key = "your_private_key_here"

[sniping]
min_liquidity = 1000
max_liquidity = 1000000
min_market_cap = 50000
max_market_cap = 5000000
max_slippage = 0.5
```

## Usage

Run the bot using:

```sh
python main.py
```

The bot will continuously monitor new token listings and execute trades when the configured conditions are met.

## How It Works

1. **Fetch Token Listings:** Retrieves token addresses from **DexScreener**.
2. **Validate Tokens:** Checks the token availability and details on **Raydium** and **Jupiter**.
3. **Apply Sniping Filters:** Ensures the token meets configured liquidity, market cap, and slippage criteria.
4. **Execute Trades:** If all conditions are met, the bot buys the token and monitors for selling opportunities.

## Logging & Monitoring

Logs are automatically generated for debugging and monitoring. You can view them in real-time with:

```sh
tail -f logs/sniper.log
```

## Disclaimer

This bot is for educational purposes only. **Use at your own risk**. Cryptocurrency trading is highly volatile, and this bot does not guarantee profits.

## License

MIT License
