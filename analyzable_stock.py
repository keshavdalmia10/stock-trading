from stock import Stock
class AnalyzableStock(Stock):
    
    def analyse(self):
        import ai_analysis
        ai_analysis.fullAnalysis(self)
