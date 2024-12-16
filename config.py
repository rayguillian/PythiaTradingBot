import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
    
    # Default trading pairs and timeframes
    TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    TIMEFRAMES = ['1h', '4h', '1d']
    
    # Risk management parameters
    MAX_POSITION_SIZE = 0.1  # 10% of portfolio
    MAX_DRAWDOWN = 0.15     # 15% maximum drawdown
    RISK_PER_TRADE = 0.01   # 1% risk per trade
