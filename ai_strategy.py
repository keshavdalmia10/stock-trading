from enum import Enum

class AIStrategy(Enum):
    GENERATE_AND_USE_CANDLESTICK_GRAPH_AND_PIVOT = "using only candlestick graph and pivot"
    GENERATE_AND_USE_STOCKDATA = "using only stock data"

class AIStrategyConfig:
    #Default strategy
    strategy = AIStrategy.GENERATE_AND_USE_STOCKDATA

    @classmethod
    def set_strategy(cls, new_strategy):
        cls.strategy = new_strategy

    @classmethod
    def get_strategy(cls):
        return cls.strategy
