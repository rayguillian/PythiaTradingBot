"""
Custom exceptions hierarchy for the Pythia Trading Bot.
These exceptions provide structured error handling throughout the application.
"""

from typing import Optional, Dict, Any

class PythiaError(Exception):
    """Base exception class for all Pythia trading bot errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary format for logging and API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }

class ExchangeError(PythiaError):
    """
    Raised when there's an error communicating with the exchange.
    
    Examples:
        - API connection failures
        - Rate limit exceeded
        - Invalid API responses
        - Order placement failures
    """
    pass

class StrategyError(PythiaError):
    """
    Raised when there's an error in strategy execution.
    
    Examples:
        - Invalid strategy parameters
        - Strategy logic failures
        - Signal generation errors
    """
    pass

class ValidationError(PythiaError):
    """
    Raised when there's a validation error in input parameters.
    
    Examples:
        - Invalid configuration values
        - Invalid trade parameters
        - Invalid data format
    """
    pass

class RiskManagementError(PythiaError):
    """
    Raised when risk management rules are violated.
    
    Examples:
        - Position size limits exceeded
        - Maximum drawdown reached
        - Daily loss limit exceeded
    """
    pass

class ConfigurationError(PythiaError):
    """
    Raised when there's an error in configuration.
    
    Examples:
        - Missing configuration files
        - Invalid configuration format
        - Missing required parameters
    """
    pass

class DataError(PythiaError):
    """
    Raised when there's an error in data handling.
    
    Examples:
        - Data fetch failures
        - Invalid data format
        - Missing required data
        - Data processing errors
    """
    pass

class SystemError(PythiaError):
    """
    Raised when there's a critical system error.
    
    Examples:
        - Memory allocation failures
        - File system errors
        - Critical resource unavailability
    """
    pass

class AuthenticationError(PythiaError):
    """
    Raised when there's an authentication or authorization error.
    
    Examples:
        - Invalid API credentials
        - Expired tokens
        - Insufficient permissions
    """
    pass

class NetworkError(PythiaError):
    """
    Raised when there's a network-related error.
    
    Examples:
        - Connection timeouts
        - DNS resolution failures
        - Network unreachability
    """
    pass