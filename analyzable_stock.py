from stock import Stock
from ai_strategy import AIStrategyConfig, AIStrategy
class AnalyzableStock(Stock):
    
    def analyse(self):
        import ai_analysis
        if(AIStrategyConfig.get_strategy() == AIStrategy.GENERATE_AND_USE_CANDLESTICK_GRAPH_AND_PIVOT):
            ai_analysis.candlestick_volume_analysis(self)
        elif(AIStrategyConfig.get_strategy() == AIStrategy.GENERATE_AND_USE_STOCKDATA):
            ai_analysis.only_stock_data_analysis(self)

    def analyseStockRating(self):
        import ai_analysis
        ai_analysis.populateStockRating(self)
