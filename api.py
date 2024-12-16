from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from backtesting.backtest_engine import BacktestEngine
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backtest engine with environment variables
backtest_engine = BacktestEngine(
    api_key=os.getenv('BINANCE_API_KEY'),
    api_secret=os.getenv('BINANCE_API_SECRET')
)

# Pydantic models for request validation
class StrategyConfigurationRequest(BaseModel):
    strategy_id: str
    parameters: Dict[str, str]

@app.get("/api/strategies")
def get_strategies() -> Dict[str, Any]:
    # Strategy definitions
    return {
        "strategies": {
            "statistical_pattern": {
                "name": "Statistical Pattern Strategy",
                "description": "Advanced quantitative strategy combining Hidden Markov Models for regime detection with statistical arbitrage",
                "status": "active",
                "parameters": {
                    "lookback_period": {
                        "name": "Lookback Period",
                        "description": "Number of days to look back for pattern analysis (trading days)",
                        "type": "number",
                        "default": 252,
                        "min": 50,
                        "max": 504
                    },
                    "regime_threshold": {
                        "name": "Regime Threshold",
                        "description": "Threshold for regime change detection (standard deviations)",
                        "type": "number",
                        "default": 1.5,
                        "min": 0.5,
                        "max": 3.0
                    },
                    "volatility_window": {
                        "name": "Volatility Window",
                        "description": "Window size for volatility calculation (trading days)",
                        "type": "number",
                        "default": 21,
                        "min": 5,
                        "max": 63
                    },
                    "num_states": {
                        "name": "Number of States",
                        "description": "Number of market regime states to identify",
                        "type": "number",
                        "default": 3,
                        "min": 2,
                        "max": 5
                    },
                    "confidence_level": {
                        "name": "Confidence Level",
                        "description": "Statistical confidence level for signal generation",
                        "type": "number",
                        "default": 0.95,
                        "min": 0.8,
                        "max": 0.99
                    }
                }
            }
        }
    }

@app.post("/api/strategies/configure")
async def configure_strategy(request: StrategyConfigurationRequest) -> Dict[str, Any]:
    try:
        # Get available strategies
        strategies = get_strategies()["strategies"]
        
        # Validate strategy exists
        if request.strategy_id not in strategies:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        strategy = strategies[request.strategy_id]
        
        # Convert parameters to float where needed
        parameters = {}
        for param_name, param_value in request.parameters.items():
            if param_name not in strategy["parameters"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid parameter: {param_name}"
                )
            
            param_config = strategy["parameters"][param_name]
            if param_config["type"] == "number":
                try:
                    value = float(param_value)
                    if "min" in param_config and value < param_config["min"]:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Parameter {param_name} below minimum value"
                        )
                    if "max" in param_config and value > param_config["max"]:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Parameter {param_name} above maximum value"
                        )
                    parameters[param_name] = value
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid number format for parameter: {param_name}"
                    )
        
        # Run backtest with the configured parameters
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)  # Last 30 days
        
        result = backtest_engine.run_backtest(
            strategy_id=request.strategy_id,
            symbol="BTCUSDT",  # Default to BTC/USDT
            interval="1h",     # Default to 1-hour timeframe
            start_time=start_time,
            end_time=end_time,
            parameters=parameters
        )
        
        return {
            "status": "success",
            "message": f"Strategy {request.strategy_id} configured and backtested successfully",
            "strategy": {
                "id": request.strategy_id,
                "name": strategy["name"],
                "parameters": parameters,
                "backtest_results": {
                    "total_return": result.total_return,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown,
                    "win_rate": result.win_rate,
                    "profit_factor": result.profit_factor
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance")
def get_performance() -> Dict[str, Any]:
    try:
        # Run backtest for the last 30 days
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        result = backtest_engine.run_backtest(
            strategy_id="statistical_pattern",
            symbol="BTCUSDT",
            interval="1h",
            start_time=start_time,
            end_time=end_time,
            parameters={
                "lookback_period": 252,
                "regime_threshold": 1.5,
                "volatility_window": 21,
                "num_states": 3,
                "confidence_level": 0.95
            }
        )
        
        # Convert trade results to API format
        recent_trades = [
            {
                "timestamp": trade.timestamp.isoformat(),
                "strategy": trade.strategy_name,
                "symbol": trade.symbol,
                "type": trade.type,
                "pnl": trade.pnl,
                "status": trade.status
            }
            for trade in result.trades[-10:]  # Get last 10 trades
        ]
        
        return {
            "summary": {
                "total_pnl": result.total_return,
                "total_trades": len(result.trades),
                "win_rate": result.win_rate,
                "current_drawdown": result.max_drawdown
            },
            "strategy_performance": [
                {
                    "strategy_name": result.strategy_name,
                    "symbol": result.symbol,
                    "interval": result.interval,
                    "total_return": result.total_return,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown,
                    "win_rate": result.win_rate,
                    "profit_factor": result.profit_factor
                }
            ],
            "recent_trades": recent_trades
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/strategy_metrics")
def get_strategy_metrics():
    # Implement endpoint to retrieve strategy metrics
    pass

@app.get("/signals")
def get_signals():
    # Implement endpoint to retrieve trading signals
    pass

@app.get("/optimization")
def get_optimization_results():
    # Implement endpoint to retrieve optimization results
    pass
