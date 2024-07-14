import threading
from typing import List
from analyzable_stock import AnalyzableStock
from kite_connector import KiteConnector
import trader as trader
import logging
from stock import Stock
logger = logging.getLogger(__name__)

class AutomateTest:
    def __init__(self, kite_connector):
        self.kite_connector : KiteConnector = kite_connector
        self.stock_list : List[Stock]= [] 
        self.high_rating_stocks : List[Stock] = []
        self.instrumentTokens = []

    def fetch_and_filter_stocks(self):
        self.high_rating_stocks.clear()
        for stock in self.stock_list:
            if stock.rating >= 8 and stock.trading_strategy == "Long":
                self.high_rating_stocks.append(stock)
                logger.warning(f'Chosen stock to automate : {stock.stock_name}')
        logger.debug("Filtered high rating stocks for trading.")

    # def trade_all_stocks(self):
    #     for stock in self.high_rating_stocks:
    #         thread = threading.Thread(target=self.trade_stock, args=(stock,), name=stock.stock_name)
    #         thread.attachedstock = stock
    #         self.threadlist.append(thread)
    #         thread.start()

    # def trade_stock(self, stock : Stock):
    #     tradable_stock_name = stock.stock_name.replace(".NS", "")
    #     instrument_token = self.kite_connector.fetch_instrument_token(tradable_stock_name) 
    #     current_price = self.kite_connector.get_current_price(instrument_token)
    #     if current_price >= stock.entry_point:
    #         print(f"Started placing order for {stock.stock_name} at {current_price}")
    #         self.kite_connector.place_stock_order(quantity=100, tradingsymbol=stock.stock_name)
    #         self.kite_connector.place_stoploss(quantity=100, stoploss_price=stock.stop_loss, tradingsymbol=stock.stock_name)
    #         self.kite_connector.place_target(quantity=100, target_price=stock.target_point, tradingsymbol=stock.stock_name)

    def populateInstrumentDic(self):
        for stock in self.high_rating_stocks:
            tradingsymbol = stock.stock_name
            intrument_token = self.kite_connector.fetch_instrument_token(tradingsymbol.replace(".NS", ""))
            self.instrumentTokens.append(intrument_token)
            self.kite_connector.intrTokenVSStock[intrument_token] = stock
        print(self.kite_connector.intrTokenVSStock)

    def addToBucket(self, stocknamelist):
        # self.stock_list = trader.populate_stocks_withAI(stocknamelist)

        stock = AnalyzableStock("DHANI.NS")
        stock.rating = 8.2
        stock.entry_point = 56.2
        stock.stop_loss = 55.48
        stock.target_point = 57.45
        stock.trading_strategy = "Long"
        self.stock_list = [stock]


        self.fetch_and_filter_stocks()
        self.populateInstrumentDic()
        # self.kite_connector.addToInstrumentList(self.instrumentTokens)
        self.kite_connector.instrumentTokensList = self.instrumentTokens
        self.kite_connector.start_web_socket()




STOCK_NAMES = ["DHANI.NS", "YESBANK.NS"]

kite_connector = KiteConnector(api_key="d2myrf8n2p720jby", api_secret="4l6bswdi9d5ti0dqki6kffoycgwpgla1")

automateTest = AutomateTest(kite_connector)
automateTest.addToBucket(STOCK_NAMES)
