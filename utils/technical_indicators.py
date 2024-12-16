import numpy as np
from typing import List
from scipy import stats

def calculate_volatility(returns: np.ndarray, window: int) -> float:
    """Calculate rolling volatility of returns.
    
    Args:
        returns (np.ndarray): Array of returns
        window (int): Rolling window size
        
    Returns:
        float: Annualized volatility
    """
    if len(returns) < window:
        return 0.0
    
    rolling_std = np.std(returns[-window:])
    return rolling_std * np.sqrt(252)  # Annualize volatility

def detect_regime(returns: np.ndarray, threshold: float) -> str:
    """Detect market regime based on returns distribution.
    
    Args:
        returns (np.ndarray): Array of returns
        threshold (float): Z-score threshold for regime detection
        
    Returns:
        str: Market regime ('trending', 'mean_reverting', or 'neutral')
    """
    if len(returns) < 2:
        return 'neutral'
    
    # Calculate basic statistics
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    skew = stats.skew(returns)
    kurtosis = stats.kurtosis(returns)
    
    # Calculate Hurst exponent
    hurst = calculate_hurst_exponent(returns)
    
    # Determine regime
    if hurst > 0.6 and abs(skew) > threshold:
        return 'trending'
    elif hurst < 0.4 and kurtosis > 3:
        return 'mean_reverting'
    else:
        return 'neutral'

def calculate_hurst_exponent(returns: np.ndarray) -> float:
    """Calculate Hurst exponent to determine time series persistence.
    
    Args:
        returns (np.ndarray): Array of returns
        
    Returns:
        float: Hurst exponent
    """
    if len(returns) < 100:
        return 0.5
    
    # Calculate various lags
    lags = range(2, min(len(returns) // 2, 20))
    
    # Calculate variance ratios
    tau = [np.sqrt(np.std(np.subtract(returns[lag:], returns[:-lag]))) 
           for lag in lags]
    
    # Perform regression
    reg = np.polyfit(np.log(lags), np.log(tau), 1)
    
    return reg[0]  # Hurst exponent is the slope

def calculate_zscore(series: np.ndarray, window: int) -> float:
    """Calculate z-score of latest value relative to rolling window.
    
    Args:
        series (np.ndarray): Time series data
        window (int): Rolling window size
        
    Returns:
        float: Z-score of latest value
    """
    if len(series) < window:
        return 0.0
    
    rolling_mean = np.mean(series[-window:])
    rolling_std = np.std(series[-window:])
    
    if rolling_std == 0:
        return 0.0
    
    return (series[-1] - rolling_mean) / rolling_std

def calculate_momentum(prices: np.ndarray, period: int) -> float:
    """Calculate momentum indicator.
    
    Args:
        prices (np.ndarray): Array of prices
        period (int): Lookback period
        
    Returns:
        float: Momentum value
    """
    if len(prices) < period:
        return 0.0
    
    return (prices[-1] / prices[-period]) - 1

def calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
    """Calculate Relative Strength Index.
    
    Args:
        prices (np.ndarray): Array of prices
        period (int): RSI period
        
    Returns:
        float: RSI value
    """
    if len(prices) < period + 1:
        return 50.0
    
    # Calculate price changes
    delta = np.diff(prices)
    
    # Separate gains and losses
    gains = np.maximum(delta, 0)
    losses = -np.minimum(delta, 0)
    
    # Calculate average gains and losses
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi
