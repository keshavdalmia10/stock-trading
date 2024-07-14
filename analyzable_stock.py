from stock import Stock
class AnalyzableStock(Stock):
    
    def analyse(self):
        import ai_analysis
        ai_analysis.candlestick_volume_analysis(self)

    def analyseStockRating(self):
        import ai_analysis
        ai_analysis.populateStockRating(self)
