from backtesting.backtest_engine import BacktestEngine
from datetime import datetime, timedelta
import os
import json

def main():
    # Initialize backtest engine
    backtest_engine = BacktestEngine(
        api_key=os.getenv('BINANCE_API_KEY'),
        api_secret=os.getenv('BINANCE_API_SECRET')
    )
    
    # Set up backtest parameters
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)
    
    # Default strategy parameters
    parameters = {
        "lookback_period": 252,
        "regime_threshold": 1.5,
        "volatility_window": 21,
        "num_states": 3,
        "confidence_level": 0.95
    }
    
    print("\nStarting backtest...")
    print(f"Period: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")
    print("Strategy: Statistical Pattern Strategy")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")
    
    try:
        # Run backtest
        result = backtest_engine.run_backtest(
            strategy_id="statistical_pattern",
            symbol="BTCUSDT",
            interval="1h",
            start_time=start_time,
            end_time=end_time,
            parameters=parameters
        )
        
        # Print results
        print("\nBacktest Results:")
        print(f"Total Return: {result.total_return:.2%}")
        print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"Max Drawdown: {result.max_drawdown:.2%}")
        print(f"Win Rate: {result.win_rate:.2%}")
        print(f"Profit Factor: {result.profit_factor:.2f}")
        
        print("\nRecent Trades:")
        for trade in result.trades[-5:]:  # Show last 5 trades
            print(f"Time: {trade.timestamp}, Type: {trade.type}, PnL: {trade.pnl:.2%}")
            
    except Exception as e:
        print(f"Error running backtest: {str(e)}")

if __name__ == "__main__":
    main()
