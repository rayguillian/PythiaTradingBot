from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OrderBook:
    bids: List[tuple[float, float]]  # price, quantity
    asks: List[tuple[float, float]]  # price, quantity
    timestamp: datetime

@dataclass
class Trade:
    symbol: str
    side: str  # 'buy' or 'sell'
    price: float
    quantity: float
    timestamp: datetime
    order_id: str
    commission: float
    commission_asset: str

@dataclass
class Position:
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    timestamp: datetime

class ExchangeBase(ABC):
    """Base class for cryptocurrency exchange implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the exchange."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the exchange."""
        pass
    
    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 100) -> OrderBook:
        """Get current orderbook for a symbol."""
        pass
    
    @abstractmethod
    async def get_balance(self, asset: str) -> float:
        """Get balance for a specific asset."""
        pass
    
    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position for a symbol."""
        pass
    
    @abstractmethod
    async def create_order(self, symbol: str, side: str, order_type: str,
                          quantity: float, price: Optional[float] = None) -> Trade:
        """Create a new order."""
        pass
    
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order."""
        pass
    
    @abstractmethod
    async def get_historical_data(self, symbol: str, interval: str,
                                start_time: datetime, end_time: datetime) -> List[Dict[str, float]]:
        """Get historical OHLCV data."""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Get current ticker information."""
        pass
