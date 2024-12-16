from typing import List, Dict
import pandas as pd

class BaseStrategy:
    def __init__(self, name: str):
        self.name = name

    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        raise NotImplementedError("Must implement generate_signals method")

class StrategyManager:
    def __init__(self):
        self.strategies = {}

    def register_strategy(self, strategy: BaseStrategy) -> None:
        self.strategies[strategy.name] = strategy

    def evaluate_strategy(self, strategy_name: str, data: pd.DataFrame) -> Dict:
        strategy = self.strategies.get(strategy_name)
        if not strategy:
            raise ValueError(f"Strategy {strategy_name} not found")
        return strategy.generate_signals(data)

    def get_signals(self, strategy_name: str, symbol: str, interval: str) -> List[Dict]:
        # Placeholder for getting signals using strategy
        pass
