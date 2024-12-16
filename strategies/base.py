from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Signal:
    symbol: str
    direction: str  # 'long', 'short', or 'neutral'
    strength: float  # 0 to 1
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class StrategyState:
    position_size: float
    current_position: str  # 'long', 'short', or 'flat'
    last_signal: Optional[Signal]
    last_update: datetime
    metadata: Dict[str, Any]

class StrategyBase(ABC):
    """Base class for trading strategies."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state = StrategyState(
            position_size=0.0,
            current_position='flat',
            last_signal=None,
            last_update=datetime.now(),
            metadata={}
        )
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize strategy with historical data if needed."""
        pass
    
    @abstractmethod
    async def generate_signal(self, market_data: Dict[str, Any]) -> Signal:
        """Generate trading signal based on market data."""
        pass
    
    @abstractmethod
    async def update_state(self, market_data: Dict[str, Any]) -> None:
        """Update strategy state with new market data."""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get current strategy parameters."""
        pass
    
    @abstractmethod
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update strategy parameters."""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate strategy parameters."""
        pass
