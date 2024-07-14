import trader as trader
import datetime
import logging
from logging_config import LogLevel, set_logging_level
logger = logging.getLogger(__name__)

set_logging_level(LogLevel.INFO)

startTime = datetime.datetime.now()

# stocklist = ["ZOMATO.NS", "RELIANCE.NS", "PNB.NS", "IDEA.NS", "YESBANK.NS", "INDUSTOWER.NS", "SAIL.NS", "BHEL.NS"]
# stocklist = ["KINGFA.NS", "SRGHFL.NS", "STCINDIA.NS", "DLINKINDIA.NS","SHIVALIK.NS", "GMBREW.NS", "CREATIVE.NS", "CASTROLIND.NS"]
# stocklist = ["IZMO.NS", "THEINVEST.NS", "ONEPOINT.NS", "DCM.NS", "HUDCO.NS", "GPPL.NS", "ZYDUSWELL.NS", "BOROLTD.NS"]
# stocklist = ["SOTL.NS", "PONNIERODE.NS", "HARSHA.NS", "SGIL.NS","PYRAMID.NS", "EMAMIPAP.NS", "PRAKASH.NS", "TVSSRICH.NS", "PITTIEING.NS"]

# stocklist = ["IDEA.NS", "YESBANK.NS", "PNB.NS", "HFCL.NS","INDUSTOWER.NS", "SAIL.NS", "INDIACEM.NS", "NHPC.NS"]
# stocklist = ["UJJIVANSFB.NS", "BHEL.NS", "CANBK.NS", "GMRINFRA.NS","ZOMATO.NS"]

stocklist = ["DHANI.NS", "YESBANK.NS"]
trader.populate_stocks_withAI(stocklist)


endTime = datetime.datetime.now()
logger.info(f'Time taken to execute : {endTime - startTime}')