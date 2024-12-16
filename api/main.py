from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import logging
from pathlib import Path
from datetime import datetime
import uvicorn
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pythia_api")

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from pythia_core import PythiaCore

# Initialize FastAPI app
app = FastAPI(title="Pythia Trading Bot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PythiaCore with environment-based configuration
config_path = os.path.join(Path(__file__).parent.parent, "config", "config.yaml")
pythia = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global pythia
    try:
        pythia = PythiaCore(config_path)
        logger.info("Pythia Trading Bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Pythia Trading Bot: {str(e)}")
        raise

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/strategies")
async def get_strategies():
    """Get list of available strategies with their configurations."""
    try:
        strategies = pythia.get_available_strategies()
        result = []
        
        for strategy_name in strategies:
            params = pythia.get_strategy_parameters(strategy_name)
            result.append({
                "name": strategy_name,
                "parameters": params
            })
            
        return result
    except Exception as e:
        logger.error(f"Error getting strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategies/{strategy_name}/configure")
async def configure_strategy(strategy_name: str, parameters: Dict[str, Any]):
    """Configure a specific strategy."""
    try:
        pythia.update_strategy_parameters(strategy_name, parameters)
        return {"status": "success", "message": f"Strategy {strategy_name} configured successfully"}
    except Exception as e:
        logger.error(f"Error configuring strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trading/start/{strategy_name}")
async def start_trading(strategy_name: str):
    """Start trading with specified strategy."""
    try:
        pythia.start_trading(strategy_name)
        return {"status": "success", "message": f"Trading started with strategy {strategy_name}"}
    except Exception as e:
        logger.error(f"Error starting trading: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trading/stop")
async def stop_trading():
    """Stop trading."""
    try:
        pythia.stop_trading()
        return {"status": "success", "message": "Trading stopped"}
    except Exception as e:
        logger.error(f"Error stopping trading: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance")
async def get_performance():
    """Get current performance metrics."""
    try:
        metrics = pythia.get_performance_metrics()
        trade_history = pythia.get_trade_history()
        metrics_history = pythia.get_metrics_history()
        
        return {
            "current_metrics": metrics,
            "trade_history": trade_history[-10:],  # Last 10 trades
            "metrics_history": metrics_history[-100:],  # Last 100 metrics points
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/exchange/info")
async def get_exchange_info():
    """Get current exchange information."""
    try:
        return pythia.get_exchange_info()
    except Exception as e:
        logger.error(f"Error getting exchange info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/performance/reset")
async def reset_performance():
    """Reset performance metrics."""
    try:
        pythia.reset_performance_metrics()
        return {"status": "success", "message": "Performance metrics reset"}
    except Exception as e:
        logger.error(f"Error resetting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
