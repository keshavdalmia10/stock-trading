import threading
from analyzable_stock import AnalyzableStock
from kite_connector import KiteConnector
import trader as trader

class AutomateTest:
    def __init__(self, kite_connector, stock_list):
        self.kite_connector = kite_connector
        self.stock_list= stock_list 
        self.high_rating_stocks = []

    def fetch_and_filter_stocks(self):

        for stock in self.stock_list:
            if stock.rating > 8 and stock.strategy == "long":
                self.high_rating_stocks.append(stock)
        print("Filtered high rating stocks for trading.")

    def trade_stocks(self):
        threads = []
        for stock in self.high_rating_stocks:
            thread = threading.Thread(target=self.trade_stock, args=(stock,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def trade_stock(self, stock):
        tradable_stock_name = stock.stock_name.replace(".NS", "")
        instrument_token = self.kite_connector.fetch_instrument_token(stock.stock_name) 
        current_price = self.kite_connector.get_current_price(instrument_token)
        if current_price >= stock.entry_point:
            print(f"Started placing order for {stock.stock_name} at {current_price}")
            self.kite_connector.place_stock_order(quantity=100, tradingsymbol=stock.stock_name)
            self.kite_connector.place_stoploss(quantity=100, stoploss_price=stock.stop_loss, tradingsymbol=stock.stock_name)
            self.kite_connector.place_target(quantity=100, target_price=stock.target_point, tradingsymbol=stock.stock_name)




STOCK_NAMES = ["HDFCLIFE.NS", "M&M.NS"]
processed_stock_list = trader.trade_stocks(STOCK_NAMES)

kite_connector = KiteConnector(api_key="d2myrf8n2p720jby", api_secret="4l6bswdi9d5ti0dqki6kffoycgwpgla1")

automateTest = AutomateTest(kite_connector,processed_stock_list)
automateTest.fetch_and_filter_stocks()
automateTest.trade_stocks()
