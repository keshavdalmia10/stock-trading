from typing import List
from analyzable_stock import AnalyzableStock
import threading
from tabulate import tabulate

def sort_stock(stocklist : List[AnalyzableStock]):
    sortedlist = sorted(stocklist, key=lambda stock: stock.rating, reverse=True)
    return sortedlist

def trade_stocks(stocknamelist : List[str]):
    stocklist = [AnalyzableStock(name) for name in stocknamelist]
    threads = []
    for stock in stocklist:
        thread = threading.Thread(target=stock.analyse)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    data = []

    sorted_stock_list = sort_stock(stocklist)

    for stock in sorted_stock_list:
        stockdata = []
        stockdata.append(stock.stock_name)
        stockdata.append(stock.trading_strategy)
        stockdata.append(stock.entry_point)
        stockdata.append(stock.target_point)
        stockdata.append(stock.stop_loss)
        stockdata.append(stock.rating)
        data.append(stockdata)
    
    headers = ["Name", "Trading Strategy", "Entry point", "Target point", "Stop loss", "Rating"]

    table = tabulate(data, headers, tablefmt="pretty")

    print(table)

