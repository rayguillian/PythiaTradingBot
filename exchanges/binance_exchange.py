from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from binance.client import AsyncClient
from binance.exceptions import BinanceAPIException
from .base import ExchangeBase, OrderBook, Trade, Position

class BinanceExchange(ExchangeBase):
    """Binance exchange implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client: Optional[AsyncClient] = None
        self.testnet = config.get('testnet', True)
        self.api_key = config['api_key']
        self.api_secret = config['api_secret']
        self._last_update_time = datetime.now()
        self._update_interval = 1.0  # seconds
        
    async def connect(self) -> None:
        """Establish connection to Binance."""
        try:
            self.client = await AsyncClient.create(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=self.testnet
            )
            # Start background tasks
            asyncio.create_task(self._update_positions())
        except BinanceAPIException as e:
            raise ConnectionError(f"Failed to connect to Binance: {str(e)}")
    
    async def disconnect(self) -> None:
        """Close connection to Binance."""
        if self.client:
            await self.client.close_connection()
            self.client = None
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> OrderBook:
        """Get current orderbook for a symbol."""
        if not self.client:
            raise ConnectionError("Not connected to Binance")
        
        try:
            depth = await self.client.get_order_book(symbol=symbol, limit=limit)
            return OrderBook(
                bids=[(float(price), float(qty)) for price, qty in depth['bids']],
                asks=[(float(price), float(qty)) for price, qty in depth['asks']],
                timestamp=datetime.now()
            )
        except BinanceAPIException as e:
            raise RuntimeError(f"Failed to get orderbook: {str(e)}")
    
    async def get_balance(self, asset: str) -> float:
        """Get balance for a specific asset."""
        if not self.client:
            raise ConnectionError("Not connected to Binance")
        
        try:
            account = await self.client.get_account()
            for balance in account['balances']:
                if balance['asset'] == asset:
                    return float(balance['free'])
            return 0.0
        except BinanceAPIException as e:
            raise RuntimeError(f"Failed to get balance: {str(e)}")
    
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position for a symbol."""
        return self.positions.get(symbol)
    
    async def create_order(self, symbol: str, side: str, order_type: str,
                          quantity: float, price: Optional[float] = None) -> Trade:
        """Create a new order."""
        if not self.client:
            raise ConnectionError("Not connected to Binance")
        
        try:
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': quantity
            }
            
            if price and order_type.upper() != 'MARKET':
                params['price'] = price
            
            order = await self.client.create_order(**params)
            
            return Trade(
                symbol=symbol,
                side=side.lower(),
                price=float(order['price']),
                quantity=float(order['executedQty']),
                timestamp=datetime.fromtimestamp(order['transactTime'] / 1000),
                order_id=order['orderId'],
                commission=float(order.get('commission', 0)),
                commission_asset=order.get('commissionAsset', '')
            )
        except BinanceAPIException as e:
            raise RuntimeError(f"Failed to create order: {str(e)}")
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order."""
        if not self.client:
            raise ConnectionError("Not connected to Binance")
        
        try:
            result = await self.client.cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            return result['status'] == 'CANCELED'
        except BinanceAPIException as e:
            raise RuntimeError(f"Failed to cancel order: {str(e)}")
    
    async def get_historical_data(self, symbol: str, interval: str,
                                start_time: datetime, end_time: datetime) -> List[Dict[str, float]]:
        """Get historical OHLCV data."""
        if not self.client:
            raise ConnectionError("Not connected to Binance")
        
        try:
            klines = await self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=str(int(start_time.timestamp() * 1000)),
                end_str=str(int(end_time.timestamp() * 1000))
            )
            
            return [{
                'timestamp': k[0] / 1000,
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5])
            } for k in klines]
        except BinanceAPIException as e:
            raise RuntimeError(f"Failed to get historical data: {str(e)}")
    
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Get current ticker information."""
        if not self.client:
            raise ConnectionError("Not connected to Binance")
        
        try:
            ticker = await self.client.get_symbol_ticker(symbol=symbol)
            return {
                'price': float(ticker['price']),
                'timestamp': datetime.now().timestamp()
            }
        except BinanceAPIException as e:
            raise RuntimeError(f"Failed to get ticker: {str(e)}")
    
    async def _update_positions(self) -> None:
        """Background task to update positions."""
        while self.client:
            try:
                account = await self.client.get_account()
                positions = {}
                
                for balance in account['balances']:
                    asset = balance['asset']
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    
                    if total > 0:
                        ticker = await self.get_ticker(f"{asset}USDT")
                        current_price = ticker['price']
                        
                        positions[f"{asset}USDT"] = Position(
                            symbol=f"{asset}USDT",
                            side='long',
                            quantity=total,
                            entry_price=0.0,  # We don't have this information
                            current_price=current_price,
                            unrealized_pnl=0.0,  # Need historical data to calculate
                            realized_pnl=0.0,  # Need historical data to calculate
                            timestamp=datetime.now()
                        )
                
                self.positions = positions
            except Exception as e:
                print(f"Error updating positions: {str(e)}")
            
            await asyncio.sleep(self._update_interval)
