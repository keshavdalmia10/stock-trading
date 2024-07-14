from enum import Enum

class PrompText(Enum):
    INITIAL_IMAGE_ANALYSIS = "Analyze candlestick patterns, noting key trends, and identifying support and resistance levels.Evaluate trading volume in relation to significant price movements for buyer or seller activity insights.Discuss the ATR to assess market volatility and its impact on trading strategies.Examine the RSI and MACD for potential market reversals or continuations and momentum changes.Combine all indicators to summarize market sentiment."
    JSON_ANALYSIS = "Analyze the provided data for the stock.(All prices are in Indian Rupees)"
    INDICATOR_ANALYSIS = "Evaluate the trading indicators shown in the image and the data on a scale from 1 to 10 for intraday trading potential. A score of 10 indicates the most favorable conditions, and a score of 1 indicates the least favorable."
    TRADING_STRATEGY = "Based on the analysis of the indicators and the candlestick chart, along with the pivot point data provided, recommend a trading strategy for intraday trading. Should I take a long position or short sell? Please also provide potential entry points, target points, stop-loss levels, rating (as discussed before), analysis_summary  in json text" 
    
    SYSTEM_PROMPT = """As a stock trader, you rely heavily on technical analysis to guide intraday trading decisions. Please analyze the provided stock chart images, focusing on candlestick patterns & volume. Based on this analysis, recommend whether to  take a long or short position for today's trading session. Additionally, rate the stock's favourability for intraday trading on a scale from 1 to 10, where 10 signifies highly favourable conditions. Provide specific trading insights including the optimal entry price, target price, and stop-loss level. Ensure your analysis is precise and supports your recommendations clearly, particularly interpreting visual data from candlestick graphs. and give the asnwer in JSON format like {"stockname":"name of stock","position":"Long or Short","entry":value,"target":value,"stoploss":value,"rating":should be out of 10(float),"analysis":"Contain summary of analysis"}"""
    USER_QUESTION = """Analyze the chart images of the stock : AAPL. Following is another data for the stock {"interval":"30m","period":"1d","pivot_points":{"classic":{"P":209.7317352294922,"R1":210.08346557617188,"R2":210.2769317626953,"R3":210.628662109375,"S1":209.53826904296875,"S2":209.18653869628906,"S3":208.99307250976562},"fibonacci":{"P":209.7317352294922,"R1":209.94000030517577,"R2":210.06866668701173,"R3":210.2769317626953,"S1":209.5234701538086,"S2":209.39480377197265,"S3":209.18653869628906}}}. Now take all the images and data in account and give the entry point, favourability, stoploss, target point for the stock. Make sure to be precise with the answer. """
    ASSISTANT_ANSWER = """{"stockname": "AAPL","position":"Long","entry":198.3,"target":205,"stoploss":190,"rating":7.5,"analysis":"The overall market sentiment appears bullish with strong upward price momentum reinforced by high trading volume. However, overbought RSI levels and decreasing ATR suggest potential short-term corrections. Traders should watch for breakouts above Rs.200 for continued bullish momentum and downside support around $192. Combining all indicators, cautious optimism is advised, with a focus on monitoring key levels and momentum shifts"}"""
    USER_PROMPT = "Analyze the chart images of the stock : {stockname}. Focus on candlestick patterns with volume. Following is another data for the stock {fibonaci_json}. Now take all the images and data in account and give the entry point, favourability, stoploss, target point for the stock. Make sure to be precise with the answer."
    def format(self, **kwargs):
        return self.value.format(**kwargs)