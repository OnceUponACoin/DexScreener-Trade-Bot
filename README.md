# **Dex Screener Trading Bot**

## **Overview**
This project is a Solana-based automated trading bot that interacts with decentralized exchanges (DEXs) to monitor and execute trades based on predefined criteria. It fetches liquidity pool data, filters pools, and executes buy/sell transactions. Telegram notifications are also supported, but will most likely be removed.

## **Features**
-  **Real-time Liquidity Pool Scanning** via DexScreener API  
-  **Customizable Sniping Filters**
-  **Automated Buy/Sell Execution** using Solana transactions  
-  **Telegram Notifications** for trade updates  
-  **Configurable via `config.ini`** for trade settings  

## **Installation & Setup**
### **1. Clone the Repository**
```sh
git clone https://github.com/OnceUponACoin/DexScreener-Trade-Bot.git
cd DexScreener-Trade-Bot
```

### **2. Install Dependencies**
Ensure you have Python installed, then run:
```sh
pip install -r requirements.txt
```

### **3. Configure `config.ini`**
- Set your Solana RPC URLs.
- Adjust filters and trading parameters.
- Add your Telegram Bot Token for notifications.

### **4. Run the Bot**
Start the trading bot:
```sh
python main.py
```

## **Security Warning**
⚠️ **Do NOT expose your private key** in `config.ini`. Use environment variables or secure vaults to protect your credentials.

## **Disclaimer**
This is an educational source code. The developers are not responsible for any financial losses or security breaches. Use at your own risk. Cryptocurrency trading is highly volatile, and past performance does not guarantee future results.

## **License**
This project is open-source under the MIT License.

