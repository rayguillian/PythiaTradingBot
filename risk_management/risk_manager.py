from typing import Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from datetime import datetime

@dataclass
class RiskMetrics:
    max_drawdown: float
    current_drawdown: float
    var_95: float
    sharpe_ratio: float
    win_rate: float
    profit_factor: float
    timestamp: datetime

class RiskManager:
    """Risk management system for trading strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize risk manager with configuration."""
        self.config = config
        self.max_drawdown_limit = config.get('max_drawdown', 0.1)
        self.max_leverage = config.get('max_leverage', 3.0)
        self.position_sizing = config.get('position_sizing', {
            'max_position_pct': 0.2,
            'risk_per_trade': 0.01
        })
        self.stop_loss = config.get('stop_loss', {
            'enabled': True,
            'type': 'trailing',
            'initial': 0.02,
            'trailing_distance': 0.01
        })
        
        # Initialize metrics
        self.reset_metrics()
        
    def reset_metrics(self) -> None:
        """Reset risk metrics."""
        self.metrics = {
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'peak_value': 1.0,
            'returns': [],
            'wins': 0,
            'losses': 0,
            'total_profit': 0.0,
            'total_loss': 0.0
        }
        
    def calculate_position_size(self, account_value: float, risk_per_trade: Optional[float] = None) -> float:
        """Calculate position size based on risk parameters."""
        max_position = account_value * self.position_sizing['max_position_pct']
        risk = risk_per_trade or self.position_sizing['risk_per_trade']
        
        # Calculate position size based on risk per trade
        position_size = account_value * risk
        
        # Ensure we don't exceed maximum position size
        return min(position_size, max_position)
        
    def update_metrics(self, current_value: float, trade_result: Optional[float] = None) -> None:
        """Update risk metrics with new portfolio value and trade result."""
        # Update drawdown metrics
        if current_value > self.metrics['peak_value']:
            self.metrics['peak_value'] = current_value
        
        current_drawdown = (self.metrics['peak_value'] - current_value) / self.metrics['peak_value']
        self.metrics['current_drawdown'] = current_drawdown
        self.metrics['max_drawdown'] = max(self.metrics['max_drawdown'], current_drawdown)
        
        # Update trade metrics if a trade was closed
        if trade_result is not None:
            if trade_result > 0:
                self.metrics['wins'] += 1
                self.metrics['total_profit'] += trade_result
            else:
                self.metrics['losses'] += 1
                self.metrics['total_loss'] += abs(trade_result)
                
            self.metrics['returns'].append(trade_result)
            
    def get_metrics(self) -> RiskMetrics:
        """Get current risk metrics."""
        total_trades = self.metrics['wins'] + self.metrics['losses']
        win_rate = self.metrics['wins'] / total_trades if total_trades > 0 else 0.0
        profit_factor = (
            self.metrics['total_profit'] / abs(self.metrics['total_loss'])
            if self.metrics['total_loss'] != 0 else float('inf')
        )
        
        # Calculate Sharpe ratio if we have returns
        if self.metrics['returns']:
            returns = np.array(self.metrics['returns'])
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) != 0 else 0.0
            var_95 = np.percentile(returns, 5) if len(returns) >= 20 else 0.0
        else:
            sharpe_ratio = 0.0
            var_95 = 0.0
            
        return RiskMetrics(
            max_drawdown=self.metrics['max_drawdown'],
            current_drawdown=self.metrics['current_drawdown'],
            var_95=var_95,
            sharpe_ratio=sharpe_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            timestamp=datetime.now()
        )
        
    def check_risk_limits(self) -> bool:
        """Check if current risk metrics are within limits."""
        if self.metrics['current_drawdown'] > self.max_drawdown_limit:
            return False
        return True
        
    def calculate_stop_loss(self, entry_price: float, position_type: str) -> float:
        """Calculate stop loss price based on configuration."""
        if not self.stop_loss['enabled']:
            return 0.0
            
        initial_stop = self.stop_loss['initial']
        if position_type == 'long':
            return entry_price * (1 - initial_stop)
        else:  # short position
            return entry_price * (1 + initial_stop)
            
    def update_trailing_stop(self, current_price: float, position_type: str, current_stop: float) -> float:
        """Update trailing stop loss price."""
        if not self.stop_loss['enabled'] or self.stop_loss['type'] != 'trailing':
            return current_stop
            
        trailing_distance = self.stop_loss['trailing_distance']
        if position_type == 'long':
            new_stop = current_price * (1 - trailing_distance)
            return max(new_stop, current_stop)
        else:  # short position
            new_stop = current_price * (1 + trailing_distance)
            return min(new_stop, current_stop)
