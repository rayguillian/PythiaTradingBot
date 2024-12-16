from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track trading performance metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize performance monitor with configuration."""
        self.config = config
        self.metrics = config.get('metrics', [
            'total_pnl',
            'win_rate',
            'sharpe_ratio',
            'max_drawdown'
        ])
        
        # Initialize performance tracking
        self.trades: List[Dict[str, Any]] = []
        self.current_value = 1.0  # Starting value normalized to 1.0
        self.peak_value = 1.0
        self.metrics_history: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.total_pnl = 0.0
        self.win_count = 0
        self.loss_count = 0
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        self.returns: List[float] = []
        
    def add_trade(self, trade: Dict[str, Any]) -> None:
        """Add a completed trade to performance tracking."""
        self.trades.append(trade)
        
        # Update metrics
        pnl = trade['realized_pnl']
        self.total_pnl += pnl
        
        if pnl > 0:
            self.win_count += 1
        else:
            self.loss_count += 1
            
        # Calculate return
        trade_return = pnl / trade['entry_value']
        self.returns.append(trade_return)
        
        # Update portfolio value
        self.current_value *= (1 + trade_return)
        
        # Update peak value and drawdown
        if self.current_value > self.peak_value:
            self.peak_value = self.current_value
        
        current_drawdown = (self.peak_value - self.current_value) / self.peak_value
        self.max_drawdown = max(self.max_drawdown, current_drawdown)
        self.current_drawdown = current_drawdown
        
        # Save metrics snapshot
        self.metrics_history.append(self.get_metrics())
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        total_trades = self.win_count + self.loss_count
        metrics = {
            'total_pnl': self.total_pnl,
            'total_trades': total_trades,
            'win_count': self.win_count,
            'loss_count': self.loss_count,
            'win_rate': self.win_count / total_trades if total_trades > 0 else 0.0,
            'max_drawdown': self.max_drawdown,
            'current_drawdown': self.current_drawdown,
            'current_value': self.current_value,
            'timestamp': datetime.now()
        }
        
        # Calculate Sharpe ratio if we have enough data
        if len(self.returns) > 1:
            returns_array = np.array(self.returns)
            metrics['sharpe_ratio'] = np.mean(returns_array) / np.std(returns_array) if np.std(returns_array) != 0 else 0.0
        else:
            metrics['sharpe_ratio'] = 0.0
            
        return metrics
        
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get complete trade history."""
        return self.trades
        
    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Get historical performance metrics."""
        return self.metrics_history
        
    def reset(self) -> None:
        """Reset all performance metrics."""
        self.trades = []
        self.current_value = 1.0
        self.peak_value = 1.0
        self.metrics_history = []
        self.total_pnl = 0.0
        self.win_count = 0
        self.loss_count = 0
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        self.returns = []
        logger.info("Performance metrics reset")
