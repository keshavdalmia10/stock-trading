from enum import Enum

class PrompText(Enum):
    INITIAL_IMAGE_ANALYSIS = "Analyze candlestick patterns, noting key trends, and identifying support and resistance levels.Evaluate trading volume in relation to significant price movements for buyer or seller activity insights.Discuss the ATR to assess market volatility and its impact on trading strategies.Examine the RSI and MACD for potential market reversals or continuations and momentum changes.Combine all indicators to summarize market sentiment."
    JSON_ANALYSIS = "Analyze the provided data for the stock.(All prices are in Indian Rupees)"
    INDICATOR_ANALYSIS = "Evaluate the trading indicators shown in the image and the data on a scale from 1 to 10 for intraday trading potential. A score of 10 indicates the most favorable conditions, and a score of 1 indicates the least favorable."
    TRADING_STRATEGY = "Based on the analysis of the indicators and the candlestick chart, along with the pivot point data provided, recommend a trading strategy for intraday trading. Should I take a long position or short sell? Please also provide potential entry points, target points, stop-loss levels, rating (as discussed before), analysis_summary  in json text" 

    def format(self, **kwargs):
        return self.value.format(**kwargs)