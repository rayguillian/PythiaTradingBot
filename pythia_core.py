import os
from typing import Dict, Any, List, Optional
import yaml
import logging
from datetime import datetime

from data_manager import DataManager
from exchange.binance_exchange import BinanceExchange
from strategies.statistical_pattern import StatisticalPatternStrategy
from monitoring.performance_monitor import PerformanceMonitor
from risk_management.risk_manager import RiskManager

logger = logging.getLogger(__name__)

class PythiaCore:
    """Core trading system that coordinates all components."""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Initialize trading system with configuration."""
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.exchange = BinanceExchange(
            api_key=os.getenv('BINANCE_API_KEY', ''),
            api_secret=os.getenv('BINANCE_API_SECRET', ''),
            testnet=os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
        )
        
        self.data_manager = DataManager()
        self.risk_manager = RiskManager(self.config['risk_management'])
        self.performance_monitor = PerformanceMonitor(self.config['performance_monitoring'])
        
        # Initialize strategies
        self.strategies = {
            'statistical_pattern': StatisticalPatternStrategy(
                self.config['strategies']['statistical_pattern']
            )
        }
        
        self.active_strategy = None
        self.is_running = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise
            
    def start_trading(self, strategy_name: str) -> None:
        """Start trading with specified strategy."""
        try:
            if strategy_name not in self.strategies:
                raise ValueError(f"Strategy {strategy_name} not found")
                
            self.active_strategy = self.strategies[strategy_name]
            self.is_running = True
            
            logger.info(f"Started trading with strategy: {strategy_name}")
            
        except Exception as e:
            logger.error(f"Error starting trading: {str(e)}")
            raise
            
    def stop_trading(self) -> None:
        """Stop trading and close positions."""
        try:
            self.is_running = False
            if self.active_strategy:
                # Close all positions
                positions = self.exchange.get_positions()
                for position in positions:
                    self.exchange.close_position(position['symbol'])
                    
            logger.info("Trading stopped, all positions closed")
            
        except Exception as e:
            logger.error(f"Error stopping trading: {str(e)}")
            raise
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_monitor.get_metrics()
        
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get trade history."""
        return self.performance_monitor.get_trade_history()
        
    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Get historical performance metrics."""
        return self.performance_monitor.get_metrics_history()
        
    def update_strategy_parameters(self, strategy_name: str, parameters: Dict[str, Any]) -> None:
        """Update strategy parameters."""
        try:
            if strategy_name not in self.strategies:
                raise ValueError(f"Strategy {strategy_name} not found")
                
            strategy = self.strategies[strategy_name]
            strategy.set_parameters(parameters)
            logger.info(f"Updated parameters for strategy: {strategy_name}")
            
        except Exception as e:
            logger.error(f"Error updating strategy parameters: {str(e)}")
            raise
            
    def get_strategy_parameters(self, strategy_name: str) -> Dict[str, Any]:
        """Get current strategy parameters."""
        try:
            if strategy_name not in self.strategies:
                raise ValueError(f"Strategy {strategy_name} not found")
                
            strategy = self.strategies[strategy_name]
            return strategy.get_parameters()
            
        except Exception as e:
            logger.error(f"Error getting strategy parameters: {str(e)}")
            raise
            
    def reset_performance_metrics(self) -> None:
        """Reset all performance metrics."""
        self.performance_monitor.reset()
        logger.info("Performance metrics reset")
        
    def get_available_strategies(self) -> List[str]:
        """Get list of available trading strategies."""
        return list(self.strategies.keys())
        
    def get_exchange_info(self) -> Dict[str, Any]:
        """Get current exchange information."""
        try:
            return {
                'exchange': self.exchange.name,
                'testnet': self.exchange.testnet,
                'trading_pairs': self.exchange.get_trading_pairs(),
                'account_balance': self.exchange.get_account_balance(),
                'positions': self.exchange.get_positions()
            }
        except Exception as e:
            logger.error(f"Error getting exchange info: {str(e)}")
            raise
