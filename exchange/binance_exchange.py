from typing import Dict, Any, List, Optional
from datetime import datetime
from binance.spot import Spot as Client
from binance.error import ClientError
from .base import ExchangeBase, ExchangeConfig, OrderStatus, OrderType, OrderSide

class BinanceExchange(ExchangeBase):
    """Binance exchange implementation."""
    
    def __init__(self, config: ExchangeConfig):
        super().__init__(config)
        self.name = "binance"
        self.client: Optional[Client] = None
        
    async def connect(self) -> None:
        """Connect to the Binance exchange."""
        try:
            # Initialize REST client
            base_url = "https://testnet.binance.vision/api" if self.config.testnet else "https://api.binance.com/api"
            self.client = Client(
                api_key=self.config.api_key,
                api_secret=self.config.api_secret,
                base_url=base_url
            )
            
            # Test connection
            server_time = self.client.time()
            self.logger.info(f"Connected to Binance. Server time: {datetime.fromtimestamp(server_time['serverTime']/1000)}")
            
        except ClientError as e:
            self.logger.error(f"Failed to connect to Binance: {str(e)}")
            raise
            
    async def get_balance(self, asset: str) -> float:
        """Get balance for a specific asset."""
        try:
            if not self.client:
                raise RuntimeError("Exchange not connected")
                
            account = self.client.account()
            for balance in account['balances']:
                if balance['asset'] == asset:
                    return float(balance['free'])
            return 0.0
            
        except ClientError as e:
            self.logger.error(f"Failed to get balance for {asset}: {str(e)}")
            raise
            
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker for a symbol."""
        try:
            if not self.client:
                raise RuntimeError("Exchange not connected")
                
            ticker = self.client.ticker_price(symbol=symbol)
            ticker_24h = self.client.ticker_24hr(symbol=symbol)
            
            return {
                'symbol': ticker['symbol'],
                'price': float(ticker['price']),
                'volume': float(ticker_24h['volume']),
                'high_24h': float(ticker_24h['highPrice']),
                'low_24h': float(ticker_24h['lowPrice']),
                'timestamp': datetime.fromtimestamp(int(ticker_24h['closeTime'])/1000)
            }
            
        except ClientError as e:
            self.logger.error(f"Failed to get ticker for {symbol}: {str(e)}")
            raise
            
    async def get_historical_data(self, symbol: str, interval: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Get historical klines/candlestick data."""
        try:
            if not self.client:
                raise RuntimeError("Exchange not connected")
                
            klines = self.client.klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            return [{
                'timestamp': datetime.fromtimestamp(k[0]/1000),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5]),
                'close_time': datetime.fromtimestamp(k[6]/1000),
                'quote_volume': float(k[7]),
                'trades': int(k[8]),
                'taker_buy_base': float(k[9]),
                'taker_buy_quote': float(k[10])
            } for k in klines]
            
        except ClientError as e:
            self.logger.error(f"Failed to get historical data for {symbol}: {str(e)}")
            raise
            
    async def place_order(self, symbol: str, side: OrderSide, type: OrderType, quantity: float, price: Optional[float] = None) -> str:
        """Place an order on the exchange."""
        try:
            if not self.client:
                raise RuntimeError("Exchange not connected")
                
            params = {
                'symbol': symbol,
                'side': side.value.upper(),
                'type': type.value.upper(),
                'quantity': quantity
            }
            
            if type == OrderType.LIMIT and price is not None:
                params['price'] = price
                params['timeInForce'] = 'GTC'
                
            order = self.client.new_order(**params)
            return order['orderId']
            
        except ClientError as e:
            self.logger.error(f"Failed to place order: {str(e)}")
            raise
            
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an existing order."""
        try:
            if not self.client:
                raise RuntimeError("Exchange not connected")
                
            self.client.cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            return True
            
        except ClientError as e:
            self.logger.error(f"Failed to cancel order {order_id}: {str(e)}")
            raise
            
    async def get_order_status(self, symbol: str, order_id: str) -> OrderStatus:
        """Get the status of an order."""
        try:
            if not self.client:
                raise RuntimeError("Exchange not connected")
                
            order = self.client.get_order(
                symbol=symbol,
                orderId=order_id
            )
            
            status_map = {
                'NEW': OrderStatus.OPEN,
                'PARTIALLY_FILLED': OrderStatus.PARTIALLY_FILLED,
                'FILLED': OrderStatus.FILLED,
                'CANCELED': OrderStatus.CANCELLED,
                'REJECTED': OrderStatus.REJECTED,
                'EXPIRED': OrderStatus.EXPIRED
            }
            
            return status_map.get(order['status'], OrderStatus.UNKNOWN)
            
        except ClientError as e:
            self.logger.error(f"Failed to get order status for {order_id}: {str(e)}")
            raise
