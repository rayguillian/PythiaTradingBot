from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime
from scipy import stats
from strategies.base import StrategyBase, Signal, StrategyState
from utils.technical_indicators import calculate_volatility, detect_regime

class StatisticalPatternStrategy(StrategyBase):
    """Implementation of the Statistical Pattern Strategy."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = config.get('name', 'statistical_pattern')
        self.parameters = config.get('parameters', {})
        self.risk_params = config.get('risk_management', {})
        self.initialize()
        
    def initialize(self) -> None:
        """Initialize strategy state and parameters."""
        self.lookback_period = self.parameters.get('lookback_period', 20)
        self.volatility_window = self.parameters.get('volatility_window', 20)
        self.entry_threshold = self.parameters.get('entry_threshold', 2.0)
        self.exit_threshold = self.parameters.get('exit_threshold', 1.0)
        self.position_size = self.parameters.get('position_size', 0.1)
        self.regime_threshold = self.parameters.get('regime_threshold', 0.5)
        self.num_states = self.parameters.get('num_states', 3)
        self.confidence_level = self.parameters.get('confidence_level', 0.95)
        
        # Initialize state
        self.state = StrategyState(
            position_size=0.0,
            current_position='flat',
            last_signal=None,
            last_update=datetime.now(),
            metadata={
                'regime': 'neutral',
                'volatility': 0.0,
                'z_score': 0.0,
                'confidence': 0.0
            }
        )
        self.historical_data: List[Dict[str, float]] = []
        
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update strategy parameters."""
        self.parameters.update(parameters)
        self.initialize()  # Reinitialize with new parameters
        
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate strategy parameters."""
        required_params = ['lookback_period', 'volatility_window', 'entry_threshold', 'exit_threshold', 'position_size', 'regime_threshold', 'num_states', 'confidence_level']
        
        # Check if all required parameters are present
        if not all(param in parameters for param in required_params):
            return False
            
        # Validate parameter values
        try:
            if parameters['lookback_period'] <= 0 or parameters['volatility_window'] <= 0:
                return False
            if parameters['entry_threshold'] <= 0 or parameters['exit_threshold'] <= 0:
                return False
            if parameters['position_size'] <= 0 or parameters['position_size'] > 1:
                return False
            if parameters['regime_threshold'] <= 0:
                return False
            if parameters['num_states'] <= 0:
                return False
            if parameters['confidence_level'] <= 0 or parameters['confidence_level'] > 1:
                return False
            return True
        except (TypeError, ValueError):
            return False
            
    def get_parameters(self) -> Dict[str, Any]:
        """Get current strategy parameters."""
        return {
            'lookback_period': self.lookback_period,
            'volatility_window': self.volatility_window,
            'entry_threshold': self.entry_threshold,
            'exit_threshold': self.exit_threshold,
            'position_size': self.position_size,
            'regime_threshold': self.regime_threshold,
            'num_states': self.num_states,
            'confidence_level': self.confidence_level
        }
        
    async def update_state(self, market_data: Dict[str, Any]) -> None:
        """Update strategy state with new market data."""
        current_price = float(market_data['close'])
        self.historical_data.append(market_data)
        
        # Keep only the required lookback period
        if len(self.historical_data) > self.lookback_period:
            self.historical_data.pop(0)
            
        # Calculate volatility if we have enough data
        if len(self.historical_data) >= self.volatility_window:
            prices = np.array([d['close'] for d in self.historical_data[-self.volatility_window:]])
            returns = np.diff(np.log(prices))
            self.state.metadata['volatility'] = np.std(returns)
            
        # Update last update timestamp
        self.state.last_update = datetime.now()
        
    async def generate_signal(self, market_data: Dict[str, Any]) -> Signal:
        """Generate trading signal based on current state."""
        if len(self.historical_data) < self.lookback_period or self.state.metadata['volatility'] is None:
            return Signal(
                symbol=market_data['symbol'],
                direction='neutral',
                strength=0.0,
                timestamp=datetime.fromtimestamp(market_data['timestamp']),
                metadata=self.state.metadata
            )
        
        prices = np.array([d['close'] for d in self.historical_data])
        returns = np.diff(np.log(prices))
        
        # Calculate z-score of current price
        z_score = (prices[-1] - np.mean(prices)) / np.std(prices)
        
        # Calculate confidence level
        confidence = 1 - stats.norm.cdf(abs(z_score))
        
        # Update metadata
        self.state.metadata.update({
            'regime': detect_regime(returns, self.regime_threshold),
            'z_score': z_score,
            'confidence': confidence
        })
        
        # Generate signal based on regime and z-score
        direction = 'neutral'
        strength = 0.0
        
        if self.state.metadata['regime'] == 'bullish' and z_score < -self.entry_threshold and confidence > self.confidence_level:
            direction = 'long'
            strength = min(1.0, abs(z_score) / (2 * self.entry_threshold))
        elif self.state.metadata['regime'] == 'bearish' and z_score > self.entry_threshold and confidence > self.confidence_level:
            direction = 'short'
            strength = min(1.0, abs(z_score) / (2 * self.entry_threshold))
        
        return Signal(
            symbol=market_data['symbol'],
            direction=direction,
            strength=strength,
            timestamp=datetime.fromtimestamp(market_data['timestamp']),
            metadata=self.state.metadata
        )
