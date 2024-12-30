import json

class Stock:

    message_history = []

    def __init__(self, stock_name):
        self._stock_name = stock_name
        self._rating = 0
        self._entry_point = 0
        self._stop_loss = 0
        self._target_point = 0
        self._trading_strategy = ""
        self._analysis = ""
        self._intrtoken = 0

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, new_rating):
        if isinstance(new_rating, (int, float)) and 0 <= new_rating <= 10:
            self._rating = new_rating
        else:
            raise ValueError("Rating must be a number between 0 and 10.")

    @property
    def intrtoken(self):
        return self._intrtoken

    @intrtoken.setter
    def intrtoken(self, new_token):
         if isinstance(new_token, (int)):
            self._intrtoken = new_token
         else:
            raise ValueError("Instrument token must be integer.")   
        
    @property
    def target_point(self):
        return self._target_point

    @target_point.setter
    def target_point(self, new_target_point):
        if isinstance(new_target_point, (int, float)) and new_target_point > 0:
            self._target_point = new_target_point
        else:
            raise ValueError("Target point must be float/integer and > 0")
        
    @property
    def stop_loss(self):
        return self._stop_loss

    @stop_loss.setter
    def stop_loss(self, new_stoploss):
        if isinstance(new_stoploss, (int, float)) and new_stoploss > 0:
            self._stop_loss = new_stoploss
        else:
            raise ValueError("Stop loss must be float/integer and > 0.")
        
    @property
    def entry_point(self):
        return self._entry_point

    @entry_point.setter
    def entry_point(self, new_entry_point):
        if isinstance(new_entry_point, (int, float)):
            self._entry_point = new_entry_point
        else:
            raise ValueError("Entry point must be float or integer.")

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
    def add_in_history(cls, message):
        cls.message_history.append(message)

    @classmethod
    def getHistory(cls):
        return cls.message_history    

    def writejson(self, json_string):
        wjson = json.loads(json_string)    
        if 'entry' in wjson:
            self.entry_point = wjson['entry']
        if 'stoploss' in wjson:
            self.stop_loss = wjson['stoploss']
        if 'target' in wjson:
            self.target_point = wjson['target']
        if 'position' in wjson:
            self.trading_strategy = wjson['position']
        if 'rating' in wjson:
            self.rating = wjson['rating']
        if 'analysis' in wjson:
            self.analysis = wjson['analysis']