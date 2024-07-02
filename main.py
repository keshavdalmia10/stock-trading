import trader as trader
import datetime
import logging
from logging_config import LogLevel, set_logging_level
logger = logging.getLogger(__name__)

set_logging_level(LogLevel.INFO)

startTime = datetime.datetime.now()

# stocklist = ["ZOMATO.NS", "RELIANCE.NS", "PNB.NS", "IDEA.NS", "YESBANK.NS", "INDUSTOWER.NS", "SAIL.NS", "BHEL.NS"]
stocklist = ["ZOMATO.NS"]
trader.trade_stocks(stocklist)


endTime = datetime.datetime.now()
logger.info(f'Time taken to execute : {endTime - startTime}')