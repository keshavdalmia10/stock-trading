from message import Message
import json
class Stock:

    message_history = []
    _rating = 0
    _entry_point= 0
    _stop_loss = 0
    _target_point = 0
    

    def __init__(self, stock_name):
        self._stock_name = stock_name
        self._trading_strategy = ""
        self._analysis = ""

    @property
    def rating(self):
        return self.__class__._rating

    @rating.setter
    def rating(self, new_rating):
        if isinstance(new_rating, (int, float)) and 0 <= new_rating <= 10:
            self.__class__._rating = new_rating
        else:
            raise ValueError("Rating must be a number between 0 and 10.")
        
        
    @property
    def target_point(self):
        return self.__class__._target_point

    @target_point.setter
    def target_point(self, new_rating):
        if isinstance(new_rating, (int, float)) and 0 <= new_rating <= 10:
            self.__class__._target_point = new_rating
        else:
            raise ValueError("Target point must be a number between 0 and 10.")
        
    @property
    def stop_loss(self):
        return self.__class__._stop_loss

    @stop_loss.setter
    def stop_loss(self, new_stoploss):
        if isinstance(new_stoploss, (int, float)) and 0 <= new_stoploss <= 10:
            self.__class__._stop_loss = new_stoploss
        else:
            raise ValueError("Stop loss must be a number between 0 and 10.")
        
    @property
    def entry_point(self):
        return self.__class__._entry_point

    @entry_point.setter
    def entry_point(self, new_entry_point):
        if isinstance(new_entry_point, (int, float)) and 0 <= new_entry_point <= 10:
            self.__class__._entry_point = new_entry_point
        else:
            raise ValueError("Entry point must be a number between 0 and 10.")

    @property
    def stock_name(self):
        return self._stock_name

    @stock_name.setter
    def stock_name(self, value):
        self._stock_name = value

    @property
    def trading_strategy(self):
        return self._trading_strategy

    @trading_strategy.setter
    def trading_strategy(self, value):
        self._trading_strategy = value

    @property
    def analysis(self):
        return self._analysis

    @analysis.setter
    def analysis(self, value):
        self._analysis = value

    @classmethod
    def add_in_history(cls, message : Message):
        cls.message_history.append(message)

    @classmethod
    def getHistory(cls):
        cls.message_history    

    @classmethod
    def writejson(cls, json_string):
        wjson = json.loads(json_string)
        cls.entry_point = wjson['entry']
        cls.stop_loss = wjson['stoploss']
        cls.target_point = wjson['target']
        cls.trading_strategy = wjson['position']
        cls.rating = wjson['rating']
        cls.analysis = wjson['analysis']



# Example usage
# stock = Stock("AAPL")
# stock.image_analysis = "Image data"
# stock.json_analysis = "JSON data"
# stock.indicator_analysis = "Indicator data"
# stock.trading_strategy = "Trading strategy data"

# print(stock.stock_name)
# print(stock.image_analysis)
# print(stock.json_analysis)
# print(stock.indicator_analysis)
# print(stock.trading_strategy)
