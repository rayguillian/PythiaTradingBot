from binance.spot import Spot
from binance.error import ClientError
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os
import logging
from typing import Dict, Optional, List, Tuple, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        """Initialize DataManager with Binance client."""
        api_key = os.getenv('BINANCE_API_KEY', '')
        api_secret = os.getenv('BINANCE_API_SECRET', '')
        base_url = "https://testnet.binance.vision/api" if os.getenv('BINANCE_TESTNET', 'true').lower() == 'true' else None
        
        self.client = Spot(
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url
        )
        self.cache = {}  # Simple in-memory cache for historical data
        self.data_validity_period = timedelta(minutes=5)  # Cache validity period
        
    def get_historical_data(self, symbol: str, interval: str, 
                          start_time: Optional[int] = None, 
                          end_time: Optional[int] = None) -> pd.DataFrame:
        """Fetch historical klines/candlestick data from Binance."""
        try:
            # Create cache key
            cache_key = f"{symbol}_{interval}_{start_time}_{end_time}"
            
            # Check cache first and validate timestamp
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if datetime.now() - cache_entry['timestamp'] < self.data_validity_period:
                    logger.info(f"Returning cached data for {cache_key}")
                    return cache_entry['data']
            
            # Fetch from Binance
            klines = self.client.klines(
                symbol=symbol,
                interval=interval,
                limit=1000,  # Maximum allowed by Binance
                startTime=start_time,
                endTime=end_time
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignored'
            ])
            
            # Clean and format data
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            # Cache the result
            self.cache[cache_key] = {
                'data': df,
                'timestamp': datetime.now()
            }
            
            return df
            
        except ClientError as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise
            
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        try:
            ticker = self.client.ticker_price(symbol=symbol)
            return float(ticker['price'])
        except ClientError as e:
            logger.error(f"Error fetching current price: {str(e)}")
            raise
            
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get current order book for a symbol."""
        try:
            return self.client.depth(symbol=symbol, limit=limit)
        except ClientError as e:
            logger.error(f"Error fetching order book: {str(e)}")
            raise
            
    def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get recent trades for a symbol."""
        try:
            return self.client.trades(symbol=symbol, limit=limit)
        except ClientError as e:
            logger.error(f"Error fetching recent trades: {str(e)}")
            raise
            
    def get_24h_stats(self, symbol: str) -> Dict:
        """Get 24-hour statistics for a symbol."""
        try:
            return self.client.ticker_24hr(symbol=symbol)
        except ClientError as e:
            logger.error(f"Error fetching 24h stats: {str(e)}")
            raise
            
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the given data."""
        # Calculate SMA
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        
        # Calculate EMA
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # Calculate MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate Bollinger Bands
        df['BB_Middle'] = df['close'].rolling(window=20).mean()
        df['BB_Upper'] = df['BB_Middle'] + 2 * df['close'].rolling(window=20).std()
        df['BB_Lower'] = df['BB_Middle'] - 2 * df['close'].rolling(window=20).std()
        
        return df
        
    def get_market_depth(self, symbol: str, levels: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get market depth and calculate order book imbalance."""
        try:
            depth = self.client.depth(symbol=symbol, limit=levels)
            
            # Convert to DataFrames
            bids_df = pd.DataFrame(depth['bids'], columns=['price', 'quantity'])
            asks_df = pd.DataFrame(depth['asks'], columns=['price', 'quantity'])
            
            # Convert to numeric
            for df in [bids_df, asks_df]:
                df['price'] = pd.to_numeric(df['price'])
                df['quantity'] = pd.to_numeric(df['quantity'])
                df['total'] = df['price'] * df['quantity']
            
            return bids_df, asks_df
            
        except ClientError as e:
            logger.error(f"Error fetching market depth: {str(e)}")
            raise
            
    def calculate_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Volume Weighted Average Price (VWAP)."""
        df['Typical_Price'] = (df['high'] + df['low'] + df['close']) / 3
        df['VP'] = df['Typical_Price'] * df['volume']
        df['VWAP'] = df['VP'].cumsum() / df['volume'].cumsum()
        return df
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe."""
        try:
            # Moving averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            df['bb_upper'] = df['bb_middle'] + 2 * df['close'].rolling(window=20).std()
            df['bb_lower'] = df['bb_middle'] - 2 * df['close'].rolling(window=20).std()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            
            # ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            df['atr'] = true_range.rolling(14).mean()
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding technical indicators: {e}")
            raise
    
    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> float:
        """Calculate historical volatility."""
        try:
            returns = np.log(df['close'] / df['close'].shift(1))
            return returns.std() * np.sqrt(252) * 100  # Annualized volatility in percentage
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            raise
    
    def detect_market_regime(self, df: pd.DataFrame, window: int = 20) -> str:
        """Detect current market regime (trending/ranging/volatile)."""
        try:
            # Calculate key metrics
            volatility = self.calculate_volatility(df, window)
            adr = (df['high'].rolling(window).mean() - df['low'].rolling(window).mean()) / df['close'].rolling(window).mean() * 100
            trend_strength = abs(df['close'].rolling(window).mean() - df['close'].rolling(window).mean().shift(1)) / df['close'].rolling(window).std()
            
            # Define regime thresholds
            if trend_strength.iloc[-1] > 1.0:
                if volatility > 30:
                    return "volatile_trend"
                return "trending"
            elif volatility > 25:
                return "volatile"
            elif adr.iloc[-1] < 1.0:
                return "low_volatility"
            else:
                return "ranging"
                
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            raise
    
    def get_order_book_imbalance(self, symbol: str, limit: int = 20) -> float:
        """Calculate order book imbalance."""
        try:
            depth = self.client.depth(symbol=symbol, limit=limit)
            
            bid_volume = sum(float(bid[1]) for bid in depth['bids'])
            ask_volume = sum(float(ask[1]) for ask in depth['asks'])
            
            total_volume = bid_volume + ask_volume
            if total_volume == 0:
                return 0
                
            return (bid_volume - ask_volume) / total_volume
            
        except Exception as e:
            logger.error(f"Error calculating order book imbalance: {e}")
            raise
    
    def get_market_summary(self, symbol: str, interval: str) -> Dict[str, Any]:
        """Get comprehensive market summary."""
        try:
            df = self.get_historical_data(symbol, interval)
            latest_price = float(df['close'].iloc[-1])
            
            return {
                'symbol': symbol,
                'price': latest_price,
                'change_24h': (latest_price - float(df['close'].iloc[-24])) / float(df['close'].iloc[-24]) * 100,
                'volume_24h': float(df['volume'].tail(24).sum()),
                'volatility': self.calculate_volatility(df),
                'regime': self.detect_market_regime(df),
                'rsi': float(df['rsi'].iloc[-1]),
                'macd': float(df['macd'].iloc[-1]),
                'order_book_imbalance': self.get_order_book_imbalance(symbol),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            raise