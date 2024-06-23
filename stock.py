from message import Message
class Stock:

    message_history = []

    def __init__(self, stock_name):
        self._stock_name = stock_name
        self._image_analysis = ""
        self._json_analysis = ""
        self._indicator_analysis = ""
        self._trading_strategy = ""

    @property
    def stock_name(self):
        return self._stock_name

    @stock_name.setter
    def stock_name(self, value):
        self._stock_name = value

    @property
    def image_analysis(self):
        return self._image_analysis

    @image_analysis.setter
    def image_analysis(self, value):
        self._image_analysis = value

    @property
    def json_analysis(self):
        return self._json_analysis

    @json_analysis.setter
    def json_analysis(self, value):
        self._json_analysis = value

    @property
    def indicator_analysis(self):
        return self._indicator_analysis

    @indicator_analysis.setter
    def indicator_analysis(self, value):
        self._indicator_analysis = value

    @property
    def trading_strategy(self):
        return self._trading_strategy

    @trading_strategy.setter
    def trading_strategy(self, value):
        self._trading_strategy = value

    @classmethod
    def add_in_history(cls, message : Message):
        cls.message_history.append(message)

    @classmethod
    def getHistory(cls):
        cls.message_history        


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
