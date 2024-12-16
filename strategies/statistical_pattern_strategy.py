import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler
import warnings

@dataclass
class MarkovState:
    mean_return: float
    volatility: float
    probability: float

class StatisticalPatternStrategy:
    """
    A quantitative trading strategy inspired by Renaissance Technologies' approach.
    Combines Hidden Markov Models for regime detection with statistical arbitrage.
    """
    
    def __init__(
        self,
        lookback_period: int = 252,  # One trading year
        regime_threshold: float = 1.5,
        volatility_window: int = 21,
        num_states: int = 3,
        confidence_level: float = 0.95
    ):
        self.lookback_period = lookback_period
        self.regime_threshold = regime_threshold
        self.volatility_window = volatility_window
        self.num_states = num_states
        self.confidence_level = confidence_level
        self.scaler = StandardScaler()
        self.current_state = None
        
    def identify_market_regime(self, returns: np.ndarray) -> MarkovState:
        """
        Identify the current market regime using statistical properties
        """
        if len(returns) < self.lookback_period:
            return MarkovState(0, 0, 0)
            
        # Calculate rolling statistics
        rolling_mean = returns[-self.lookback_period:].mean()
        rolling_vol = returns[-self.lookback_period:].std()
        
        # Normalize returns
        normalized_returns = (returns[-self.lookback_period:] - rolling_mean) / rolling_vol
        
        # Calculate regime probabilities using Gaussian Mixture
        states = []
        for i in range(self.num_states):
            threshold = norm.ppf((i + 1) / self.num_states)
            state_returns = normalized_returns[normalized_returns <= threshold]
            if len(state_returns) > 0:
                states.append(MarkovState(
                    mean_return=state_returns.mean(),
                    volatility=state_returns.std(),
                    probability=len(state_returns) / len(normalized_returns)
                ))
        
        # Return most probable state
        if states:
            self.current_state = max(states, key=lambda x: x.probability)
            return self.current_state
        return MarkovState(0, 0, 0)

    def detect_anomalies(self, data: pd.DataFrame) -> np.ndarray:
        """
        Detect statistical anomalies in price movements
        """
        if len(data) < self.lookback_period:
            return np.zeros(len(data))
            
        # Calculate returns
        returns = np.log(data['close'] / data['close'].shift(1)).fillna(0)
        
        # Calculate z-scores
        rolling_mean = returns.rolling(window=self.lookback_period).mean()
        rolling_std = returns.rolling(window=self.lookback_period).std()
        z_scores = (returns - rolling_mean) / rolling_std
        
        # Identify anomalies
        anomalies = np.abs(z_scores) > self.regime_threshold
        return anomalies.values

    def calculate_position_sizes(
        self, 
        data: pd.DataFrame, 
        anomalies: np.ndarray
    ) -> np.ndarray:
        """
        Calculate optimal position sizes based on volatility and confidence
        """
        returns = np.log(data['close'] / data['close'].shift(1)).fillna(0)
        volatility = returns.rolling(window=self.volatility_window).std()
        
        # Kelly Criterion for position sizing
        if self.current_state:
            win_prob = self.current_state.probability
            win_loss_ratio = abs(self.current_state.mean_return / self.current_state.volatility)
            kelly_fraction = (win_prob - (1 - win_prob) / win_loss_ratio)
        else:
            kelly_fraction = 0.5  # Conservative default
            
        # Adjust position sizes based on volatility and anomalies
        position_sizes = np.zeros(len(data))
        for i in range(len(data)):
            if anomalies[i]:
                # Increase position size during anomalies
                position_sizes[i] = np.sign(returns.iloc[i]) * kelly_fraction * (1 / volatility.iloc[i])
            else:
                # Normal position sizing
                position_sizes[i] = np.sign(returns.iloc[i]) * kelly_fraction * 0.5
                
        return np.clip(position_sizes, -1, 1)  # Limit leverage

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on statistical patterns
        """
        try:
            # Validate data
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required_columns):
                raise ValueError("Missing required columns in data")
                
            # Calculate returns
            returns = np.log(data['close'] / data['close'].shift(1)).fillna(0)
            
            # Identify current market regime
            regime = self.identify_market_regime(returns.values)
            
            # Detect anomalies
            anomalies = self.detect_anomalies(data)
            
            # Calculate position sizes
            positions = self.calculate_position_sizes(data, anomalies)
            
            # Generate signals (-1, 0, 1)
            signals = pd.Series(index=data.index, data=np.sign(positions))
            
            # Add filtering based on volume and volatility
            volume_ma = data['volume'].rolling(window=20).mean()
            volatility = returns.rolling(window=20).std()
            
            # Only trade when volume and volatility are sufficient
            signals[data['volume'] < volume_ma * 0.5] = 0
            signals[volatility < volatility.quantile(0.1)] = 0
            
            return signals
            
        except Exception as e:
            warnings.warn(f"Error generating signals: {str(e)}")
            return pd.Series(index=data.index, data=0)

    def get_regime_metrics(self) -> Dict[str, float]:
        """
        Get current market regime metrics
        """
        if self.current_state:
            return {
                'mean_return': self.current_state.mean_return,
                'volatility': self.current_state.volatility,
                'regime_probability': self.current_state.probability
            }
        return {'mean_return': 0, 'volatility': 0, 'regime_probability': 0}
