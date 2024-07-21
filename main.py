import trader as trader
import datetime
import logging
from logging_config import LogLevel, set_logging_level
from ai_strategy import AIStrategy, AIStrategyConfig
logger = logging.getLogger(__name__)

set_logging_level(LogLevel.INFO)

startTime = datetime.datetime.now()

# stocklist = ["ZOMATO", "RELIANCE", "PNB", "IDEA", "YESBANK", "INDUSTOWER", "SAIL", "BHEL"]
# stocklist = ["KINGFA", "SRGHFL", "STCINDIA", "DLINKINDIA","SHIVALIK", "GMBREW", "CREATIVE", "CASTROLIND"]
# stocklist = ["IZMO", "THEINVEST", "ONEPOINT", "DCM", "HUDCO", "GPPL", "ZYDUSWELL", "BOROLTD"]
# stocklist = ["SOTL", "PONNIERODE", "HARSHA", "SGIL","PYRAMID", "EMAMIPAP", "PRAKASH", "TVSSRICH", "PITTIEING"]

# stocklist = ["IDEA", "YESBANK", "PNB", "HFCL","INDUSTOWER", "SAIL", "INDIACEM", "NHPC"]
# stocklist = ["UJJIVANSFB", "BHEL", "CANBK", "GMRINFRA","ZOMATO"]
stocklist = ['ITC']
# trader.get_tradable_stocklist(stocklist)
trader.populateStockNamesWithAI(stocklist)


endTime = datetime.datetime.now()
logger.info(f'Time taken to execute : {endTime - startTime}')