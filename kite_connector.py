import json
import os
from datetime import datetime, timedelta
from kiteconnect import KiteConnect, KiteTicker
from stock import Stock
import logging
logger = logging.getLogger(__name__)

class KiteConnector:
    def __init__(self, api_key, api_secret, session_file="kite_session.json"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session_file = session_file
        self.kite = KiteConnect(api_key=api_key)
        self._load_session()
        self.intrTokenVSStock = {}
        self.instrumentTokensList = []
        self.kws = None

    def datetime_handler(self, x):
        if isinstance(x, datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    def save_session(self, data):
        data = json.dumps(data, default=self.datetime_handler)
        with open(self.session_file, "w") as file:
            file.write(data)

    def load_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, "r") as file:
                data = json.load(file)
                if 'expiry' in data:
                    data['expiry'] = datetime.fromisoformat(data['expiry'])
                return data
        return None

    def _load_session(self):
        session_data = self.load_session()
        if session_data and session_data.get("access_token") and (session_data.get("expiry") and session_data.get("expiry") > datetime.now()):
            self.kite.set_access_token(session_data["access_token"])
            print("Using saved access token.")
        else:
            self._authenticate()

    def _authenticate(self):
        print("No valid session found, require login.")
        print("Visit this URL to login:", self.kite.login_url())
        request_token = input("Enter the request token: ")
        data = self.kite.generate_session(request_token, api_secret=self.api_secret)
        self.kite.set_access_token(data["access_token"])
        data['expiry'] = datetime.now() + timedelta(days=1)
        self.save_session(data)

    def get_kite_client(self):
        return self.kite
    
    def place_stoploss(self, quantity, stoploss_price, tradingsymbol):
        try: 
            stoploss_order_id = self.kite.place_order(
            tradingsymbol=tradingsymbol,
            exchange=self.kite.EXCHANGE_NSE,
            transaction_type=self.kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_SL,
            price=stoploss_price,
            trigger_price=stoploss_price,
            product=self.kite.PRODUCT_MIS,
            variety=self.kite.VARIETY_REGULAR
    )
        except Exception as e:
            logger.warning(f"Stoploss placing error for {tradingsymbol} : {str(e)}")

    def place_target(self, quantity, target_price, tradingsymbol):
        try: 
            target_order_id = self.kite.place_order(
            tradingsymbol=tradingsymbol,
            exchange=self.kite.EXCHANGE_NSE,
            transaction_type=self.kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_LIMIT,
            price=target_price,
            product=self.kite.PRODUCT_MIS,
            variety=self.kite.VARIETY_REGULAR
    )
        except Exception as e:
            logger.warning(f"Target placing error for {tradingsymbol} : {str(e)}")

    def place_stock_order(self, quantity, tradingsymbol):
        try:
            order_id = self.kite.place_order(tradingsymbol=tradingsymbol,
                                        variety=self.kite.VARIETY_REGULAR,
                                        exchange=self.kite.EXCHANGE_NSE,
                                        transaction_type=self.kite.TRANSACTION_TYPE_BUY,
                                        quantity=quantity,
                                        order_type=self.kite.ORDER_TYPE_MARKET,
                                        product=self.kite.PRODUCT_MIS)
            logger.info(f"Order placed. ID is: {order_id}")
        except Exception as e:
            logger.warning(f"Purchase error for {tradingsymbol} : {str(e)}")

    def fetch_instrument_token(self, tradingsymbol):
        try:
            instruments = self.kite.instruments(exchange=self.kite.EXCHANGE_NSE)
            for instrument in instruments:
                if instrument['tradingsymbol'] == tradingsymbol:
                    print(f"Found {tradingsymbol}: Token = {instrument['instrument_token']}, Name = {instrument['name']}")
                    return instrument['instrument_token']
        except Exception as e:
            print(f"Failed to fetch instruments: {str(e)}")
        return None
    
    def live_balance(self):
        margins = self.kite.margins(segment="equity")
        live_balance = margins['available']['live_balance']
        return live_balance

    def on_ticks(self, ws, ticks):
        print("Ticks received")
        for tick in ticks:
            instrument_token = tick['instrument_token']
            stock = self.intrTokenVSStock[instrument_token]
            last_price = tick['last_price']
            stock_entry = stock.entry_price
            stock_stoploss = stock.stop_loss
            stock_target = stock.target_point
            stock_name = stock.stock_name
            tradable_stock_name = stock_name.replace(".NS", "")
            print(f'Last price : {stock_name} - {last_price}')

    def on_connect(self, ws, response):
        print("WebSocket connected")
        ws.subscribe(self.instrumentTokensList)
        ws.set_mode(ws.MODE_FULL, self.instrumentTokensList)

    def on_close(self, ws, code, reason):
        print(f"WebSocket closed: {code} | {reason}")

    def start_web_socket(self):
        session_data = self.load_session()
        self.kws = KiteTicker(self.api_key, session_data["access_token"])
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.connect(threaded=True)

    def updateInstrumentListForBought(self, instrument_bought):
        new_instrumentTokenlist = list(self.instrumentTokensList)
        self.kws.unsubscribe(self.instrumentTokensList)
        new_instrumentTokenlist.remove(instrument_bought)
        self.instrumentTokensList = new_instrumentTokenlist
        self.kws.subscribe(self.instrumentTokensList)
        self.kws.set_mode(self.kws.MODE_FULL, self.instrumentTokensList)

    def addToInstrumentList(self,newInstrumentTokenList):
        session_data = self.load_session()
        self.kws = KiteTicker(self.api_key, session_data["access_token"])
        if len(self.instrumentTokensList) == 0:
            self.instrumentTokensList.extend(newInstrumentTokenList)
        else:
            self.kws.unsubscribe(self.instrumentTokensList)
            self.instrumentTokensList.extend(newInstrumentTokenList)
        self.kws.subscribe(self.instrumentTokensList)
        self.kws.set_mode(self.kws.MODE_FULL, self.instrumentTokensList)
