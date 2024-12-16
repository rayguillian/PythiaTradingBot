import uvicorn
import os
from pathlib import Path

# Ensure required directories exist
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
