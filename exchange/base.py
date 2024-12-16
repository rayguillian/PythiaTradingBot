from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

@dataclass
class ExchangeConfig:
    """Exchange configuration."""
    name: str
    testnet: bool
    api_key: str
    api_secret: str
    rate_limits: Dict[str, int]

class OrderType(Enum):
    """Order types supported by exchanges."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderSide(Enum):
    """Order sides supported by exchanges."""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    """Order statuses supported by exchanges."""
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNKNOWN = "unknown"

class ExchangeBase(ABC):
    """Base class for exchange implementations."""
    
    def __init__(self, config: ExchangeConfig):
        self.config = config
        self.logger = logging.getLogger(f"exchange.{config.name}")
        
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the exchange."""
        pass
        
    @abstractmethod
    async def get_balance(self, asset: str) -> float:
        """Get balance for a specific asset."""
        pass
        
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker for a symbol."""
        pass
        
    @abstractmethod
    async def get_historical_data(self, symbol: str, interval: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Get historical klines/candlestick data."""
        pass
        
    @abstractmethod
    async def place_order(self, symbol: str, side: OrderSide, type: OrderType, quantity: float, price: Optional[float] = None) -> str:
        """Place an order on the exchange."""
        pass
        
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order."""
        pass
        
    @abstractmethod
    async def get_order_status(self, symbol: str, order_id: str) -> OrderStatus:
        """Get the status of an order."""
        pass
