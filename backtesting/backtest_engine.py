import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from binance.client import Client
from dataclasses import dataclass
import logging
from strategies.statistical_pattern_strategy import StatisticalPatternStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradeResult:
    timestamp: datetime
    strategy_name: str
    symbol: str
    type: str  # 'LONG' or 'SHORT'
    entry_price: float
    exit_price: float
    pnl: float
    status: str  # 'OPEN' or 'CLOSED'

@dataclass
class BacktestResult:
    strategy_name: str
    symbol: str
    interval: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    trades: List[TradeResult]

class BacktestEngine:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize the backtest engine with optional Binance credentials"""
        self.client = Client(api_key, api_secret) if api_key and api_secret else Client()
        self.strategies = {
            'statistical_pattern': StatisticalPatternStrategy
        }
    
    def fetch_historical_data(
        self, 
        symbol: str, 
        interval: str, 
        start_time: datetime,
        end_time: datetime
    ) -> pd.DataFrame:
        """Fetch historical klines data from Binance"""
        try:
            klines = self.client.get_historical_klines(
                symbol,
                interval,
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignored'
            ])
            
            # Convert timestamps to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Convert string values to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
                
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise
    
    def calculate_metrics(
        self,
        trades: List[TradeResult],
        data: pd.DataFrame
    ) -> Tuple[float, float, float, float, float]:
        """Calculate performance metrics from trade results"""
        if not trades:
            return 0.0, 0.0, 0.0, 0.0, 0.0
            
        # Calculate returns
        returns = [trade.pnl for trade in trades]
        total_return = sum(returns)
        
        # Calculate Sharpe ratio (assuming risk-free rate = 0)
        returns_series = pd.Series(returns)
        sharpe_ratio = np.sqrt(252) * (returns_series.mean() / returns_series.std()) if len(returns) > 1 else 0
        
        # Calculate maximum drawdown
        cumulative_returns = (1 + returns_series).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        max_drawdown = drawdowns.min()
        
        # Calculate win rate
        winning_trades = sum(1 for trade in trades if trade.pnl > 0)
        win_rate = winning_trades / len(trades) if trades else 0
        
        # Calculate profit factor
        gross_profits = sum(pnl for pnl in returns if pnl > 0)
        gross_losses = abs(sum(pnl for pnl in returns if pnl < 0))
        profit_factor = gross_profits / gross_losses if gross_losses != 0 else float('inf')
        
        return total_return, sharpe_ratio, max_drawdown, win_rate, profit_factor
    
    def run_backtest(
        self,
        strategy_id: str,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime,
        parameters: Dict[str, float]
    ) -> BacktestResult:
        """Run backtest for a specific strategy"""
        try:
            # Fetch historical data
            data = self.fetch_historical_data(symbol, interval, start_time, end_time)
            
            # Initialize strategy
            if strategy_id not in self.strategies:
                raise ValueError(f"Strategy {strategy_id} not found")
                
            strategy_class = self.strategies[strategy_id]
            strategy = strategy_class(**parameters)
            
            # Generate signals
            signals = strategy.generate_signals(data)
            
            # Initialize variables for trade simulation
            position = 0
            trades: List[TradeResult] = []
            entry_price = 0.0
            
            # Simulate trades
            for i in range(1, len(data)):
                current_signal = signals.iloc[i]
                
                # Check for entry conditions
                if position == 0 and current_signal != 0:
                    position = 1 if current_signal > 0 else -1
                    entry_price = data.iloc[i]['close']
                    
                # Check for exit conditions
                elif position != 0 and (current_signal == 0 or current_signal == -position):
                    exit_price = data.iloc[i]['close']
                    pnl = position * (exit_price - entry_price) / entry_price
                    
                    trades.append(TradeResult(
                        timestamp=data.iloc[i]['timestamp'],
                        strategy_name=strategy_id,
                        symbol=symbol,
                        type='LONG' if position > 0 else 'SHORT',
                        entry_price=entry_price,
                        exit_price=exit_price,
                        pnl=pnl,
                        status='CLOSED'
                    ))
                    
                    position = 0
                    entry_price = 0.0
            
            # Calculate performance metrics
            total_return, sharpe_ratio, max_drawdown, win_rate, profit_factor = self.calculate_metrics(trades, data)
            
            return BacktestResult(
                strategy_name=strategy_id,
                symbol=symbol,
                interval=interval,
                total_return=total_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                trades=trades
            )
            
        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            raise
