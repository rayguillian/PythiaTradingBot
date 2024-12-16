# Pythia Trading Bot

Pythia is a modular cryptocurrency trading system that uses the Binance API for data and trading. The system tests multiple trading strategies across different trading pairs and timeframes, allows paper trading for validation, and can be deployed for live trading after thorough testing.

## Setup

1. Clone the repository.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Binance API keys in the environment variables `BINANCE_API_KEY` and `BINANCE_API_SECRET`.
4. Run the bot:
   ```bash
   python pythia_core.py
   ```

## Project Structure
- `pythia_core.py`: Core orchestration and configuration management.
- `data_manager.py`: Handles data fetching and caching.
- `requirements.txt`: Lists the required Python packages.

## Configuration
Configuration is managed through YAML files located in the `config/` directory.
