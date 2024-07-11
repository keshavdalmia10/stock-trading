import json
import os
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
import logging
logger = logging.getLogger(__name__)

class KiteConnector:
    def __init__(self, api_key, api_secret, session_file="kite_session.json"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session_file = session_file
        self.kite = KiteConnect(api_key=api_key)
        self._load_session()

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
            trigger_price=stoploss_price,  # Adjust based on your broker's requirement
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
        # available_cash = margins['available']['cash']
        # net = margins['net']
        live_balance = margins['available']['live_balance']
        live_balance = margins['available']['live_balance']
        return live_balance

    def on_ticks(self, ws, ticks):
        # Fetch and print the current price
        self.current_price = ticks[0]['last_price']
        print(f"Current price: {self.current_price}")

    def on_connect(self, ws, response):
        # Subscribe to the desired instrument
        ws.subscribe([self.instrument_token])
        ws.set_mode(ws.MODE_FULL, [self.instrument_token])

    def on_close(self, ws, code, reason):
        print(f"WebSocket closed: {code} | {reason}")

    def get_current_price(self):
        # Method to access the current price externally
        return self.current_price

    def socket(self):
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.connect(threaded=True)