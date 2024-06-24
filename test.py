from analyzable_stock import AnalyzableStock
from multithreading import generate_all_charts_for_stock

import ai_analysis
#Uncomment below line to analyze a stock
stock = AnalyzableStock("ZOMATO.NS")
ai_analysis.optimized_full_analysis(stock)
# stock.analyse()

#Uncomment below line to check chart creation
# generate_all_charts_for_stock("ZOMATO.NS")
