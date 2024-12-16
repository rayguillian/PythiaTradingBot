import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import json
from typing import Optional, Dict, Any

class TradingLogger:
    """
    Advanced logging system for the trading bot with rotating file handlers
    and structured logging capabilities.
    """
    
    def __init__(
        self,
        name: str = "PythiaTrader",
        log_level: int = logging.INFO,
        log_dir: str = "logs",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Remove any existing handlers
        self.logger.handlers = []
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(console_handler)
        
        # Main log file with size-based rotation
        main_handler = RotatingFileHandler(
            filename=self.log_dir / "pythia.log",
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        main_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(main_handler)
        
        # Trade log file with time-based rotation (daily)
        trade_handler = TimedRotatingFileHandler(
            filename=self.log_dir / "trades.log",
            when="midnight",
            interval=1,
            backupCount=30  # Keep 30 days of trade logs
        )
        trade_handler.setFormatter(self._get_formatter())
        trade_handler.addFilter(lambda record: record.name == "trades")
        self.logger.addHandler(trade_handler)
        
        # Error log file
        error_handler = RotatingFileHandler(
            filename=self.log_dir / "errors.log",
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(error_handler)
        
    @staticmethod
    def _get_formatter() -> logging.Formatter:
        """Create a detailed log formatter."""
        return logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
        )
        
    def _log_structured(
        self,
        level: int,
        message: str,
        event_type: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a structured message with additional metadata."""
        structured_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "message": message,
            "data": additional_data or {}
        }
        self.logger.log(level, json.dumps(structured_data))
        
    def log_trade(
        self,
        trade_type: str,
        symbol: str,
        amount: float,
        price: float,
        strategy: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log trade execution with detailed information."""
        trade_data = {
            "trade_type": trade_type,
            "symbol": symbol,
            "amount": amount,
            "price": price,
            "strategy": strategy,
            **additional_data or {}
        }
        self._log_structured(
            logging.INFO,
            f"{trade_type} {amount} {symbol} @ {price}",
            "trade_execution",
            trade_data
        )
        
    def log_error(
        self,
        error: Exception,
        context: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log detailed error information."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            **additional_data or {}
        }
        self._log_structured(
            logging.ERROR,
            f"Error in {context}: {str(error)}",
            "error",
            error_data
        )
        
    def log_strategy(
        self,
        strategy_name: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log strategy-related events."""
        strategy_data = {
            "strategy": strategy_name,
            "action": action,
            "parameters": parameters or {}
        }
        self._log_structured(
            logging.INFO,
            f"Strategy {strategy_name}: {action}",
            "strategy_event",
            strategy_data
        )
        
    def log_performance(
        self,
        metrics: Dict[str, Any]
    ) -> None:
        """Log performance metrics."""
        self._log_structured(
            logging.INFO,
            "Performance update",
            "performance_metrics",
            metrics
        )

# Global logger instance
trading_logger = TradingLogger()