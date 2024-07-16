from typing import List
from analyzable_stock import AnalyzableStock
import threading
from tabulate import tabulate
import logging
logger = logging.getLogger(__name__)

def sort_stock(stocklist : List[AnalyzableStock]):
    sortedlist = sorted(stocklist, key=lambda stock: stock.rating, reverse=True)
    return sortedlist

def populateStockNamesWithAI(stocknamelist : List[str]):
    stocklist = [AnalyzableStock(name + ".NS") for name in stocknamelist]
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

    return stocklist

def get_tradable_stocklist(stocklist : List[str]):

    if not stocklist:
        return []

    ratedstocks = populate_stockRating_withAI(stocklist)

    threads = []
    for stock in ratedstocks:
        thread = threading.Thread(target=stock.analyse)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    data = []

    sorted_stock_list = sort_stock(ratedstocks)

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

    filtered_stocks = [stock for stock in sorted_stock_list if stock.rating >= 7 and stock.entry_point > 0 and stock.stop_loss > 0 and stock.target_point > 0]

    return filtered_stocks



def populate_stockRating_withAI(stocknamelist : List[str]):
    stocklist = [AnalyzableStock(name + ".NS") for name in stocknamelist]
    threads = []
    for stock in stocklist:
        thread = threading.Thread(target=stock.analyseStockRating)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    data = []

    sorted_stock_list = sort_stock(stocklist)

    for stock in sorted_stock_list:
        stockdata = []
        stockdata.append(stock.stock_name)
        stockdata.append(stock.trading_strategy)
        stockdata.append(stock.rating)
        data.append(stockdata)
    
    headers = ["Name", "Trading Strategy", "Rating"]

    table = tabulate(data, headers, tablefmt="pretty")

    print(table)

    filtered_stocks = [stock for stock in stocklist if stock.rating >= 6]

    print("Filtering the following stocks")
    for stock in filtered_stocks:
        print(stock.stock_name)

    return filtered_stocks