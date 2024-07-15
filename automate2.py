from kiteconnect import KiteConnect, KiteTicker
import os
import json
from datetime import datetime, timedelta
import threading

# Define your API key and secret
api_key = "d2myrf8n2p720jby"
api_secret = "4l6bswdi9d5ti0dqki6kffoycgwpgla1"

session_file = "kite_session.json"

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def save_session(data):
    # Convert all datetime objects to strings before saving
    data = json.dumps(data, default=datetime_handler)
    with open(session_file, "w") as file:
        file.write(data)

def load_session():
    if os.path.exists(session_file):
        with open(session_file, "r") as file:
            data = json.load(file)
            if 'expiry' in data:
                data['expiry'] = datetime.fromisoformat(data['expiry'])
            return data
    return None

# Initialize KiteConnect client
kite = KiteConnect(api_key=api_key)

# Try to load the existing access token
session_data = load_session()
if session_data and session_data.get("access_token") and (session_data.get("expiry") and session_data.get("expiry") > datetime.now()):
    kite.set_access_token(session_data["access_token"])
    print("Using saved access token.")
else:
    print("No valid session found, require login.")
    print("Visit this URL to login:", kite.login_url())
    request_token = input("Enter the request token: ")
    data = kite.generate_session(request_token, api_secret=api_secret)
    kite.set_access_token(data["access_token"])
    # Update data with expiry
    data['expiry'] = datetime.now() + timedelta(days=1)
    save_session(data)



# # Fetch all instruments
# try:
#     instruments = kite.instruments(exchange=kite.EXCHANGE_NSE)
#     # Filter for a specific stock by its trading symbol and exchange
#     for instrument in instruments:
#         if instrument['tradingsymbol'] == tradingsymbol:
#             print(f"Found Infosys: Token = {instrument['instrument_token']}, Name = {instrument['name']}")
# except Exception as e:
#     print(f"Failed to fetch instruments: {str(e)}")

def place_stoploss(quantity, stoploss_price, tradingsymbol):
        stoploss_order_id = kite.place_order(
        tradingsymbol=tradingsymbol,
        exchange=kite.EXCHANGE_NSE,
        transaction_type=kite.TRANSACTION_TYPE_SELL,
        quantity=quantity,
        order_type=kite.ORDER_TYPE_SL,
        price=stoploss_price,
        trigger_price=stoploss_price,  # Adjust based on your broker's requirement
        product=kite.PRODUCT_MIS,
        variety=kite.VARIETY_REGULAR
)
        return stoploss_order_id

def place_target(quantity, target_price, tradingsymbol):
        target_order_id = kite.place_order(
        tradingsymbol=tradingsymbol,
        exchange=kite.EXCHANGE_NSE,
        transaction_type=kite.TRANSACTION_TYPE_SELL,
        quantity=quantity,
        order_type=kite.ORDER_TYPE_LIMIT,
        price=target_price,
        product=kite.PRODUCT_MIS,
        variety=kite.VARIETY_REGULAR
)
        return target_order_id

# try:
#     target_id = place_target(1, 54, "DHANI")
#     print(f'Target added : {target_id}')
# except Exception as e:
#             print(f"An error occurred while placing the order: {str(e)}")

margins = kite.margins(segment="equity")  # Use "commodity" for commodity segment

available_cash = margins['available']['cash']
live_balance = margins['available']['live_balance']
net = margins['net']
print(f"Available cash: {available_cash}")
print(f"net balance : {net}")
print(f'Live balance : {live_balance}')

# You can also print the complete margins dictionary to see all available details
# print(margins)



while(True):
    entry_price = float(input("Enter the entry price: "))
    instrument_token = 3938305  # Example token for Infosys; replace with your stock's token

    # Function to place an order
    def place_order():
        try:
            order_id = kite.place_order(tradingsymbol="RELIANCE",
                                        variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NSE,
                                        transaction_type=kite.TRANSACTION_TYPE_BUY,
                                        quantity=1,
                                        order_type=kite.ORDER_TYPE_MARKET,
                                        product=kite.PRODUCT_MIS)
            print(f"Order placed. ID is: {order_id}")
        except Exception as e:
            print(f"An error occurred while placing the order: {str(e)}")

    # Callback for tick reception
    def on_ticks(ws, ticks):
        # Check if the current price is equal to the entry price
        current_price = ticks[0]['last_price']
        print(f"Current price: {current_price}")
        # if current_price <= entry_price:
        #     print("Target price reached, placing order...")
        #     # place_order()
        ws.close()

    def on_connect(ws, response):
        ws.subscribe([instrument_token])
        ws.set_mode(ws.MODE_FULL, [instrument_token])

    def on_close(ws, code, reason):
        print(f"WebSocket closed: {code} | {reason}")

    # Starting the KiteTicker to get live market data
    kws = KiteTicker(api_key, session_data["access_token"])

    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close

    # Start the WebSocket in a new thread
    thread = threading.Thread(target=kws.connect)
    thread.start()