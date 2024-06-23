from enum import Enum

class PrompText(Enum):
    INITIAL_IMAGE_ANALYSIS = "Please analyze the candlestick chart and additional indicators shown in the image for the stock {tickername}. Focus specifically on intraday trading patterns"
    JSON_ANALYSIS = "Analyze the provided JSON data for pivot points, including both classic and Fibonacci levels."
    INDICATOR_ANALYSIS = "Evaluate the trading indicators shown in the image and the pivot points from the JSON data on a scale from 1 to 10 for intraday trading potential. A score of 10 indicates the most favorable conditions, and a score of 1 indicates the least favorable."
    TRADING_STRATEGY = "Based on the analysis of the indicators and the candlestick chart, along with the pivot point data from the JSON, recommend a trading strategy for intraday trading. Should I take a long position or short sell? Please also provide potential entry points, target points, and stop-loss levels." 

    def format(self, **kwargs):
        return self.value.format(**kwargs)