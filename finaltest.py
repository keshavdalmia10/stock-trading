import time
from kiteconnect import KiteTicker
from threading import Thread

# Initialize KiteTicker with your API key and access token
api_key = "d2myrf8n2p720jby"
api_secret = "4l6bswdi9d5ti0dqki6kffoycgwpgla1"
access_token = "rY8rD5HJOlZjCItm9zko3UGpTBOn5tk2"
kite_ticker = KiteTicker(api_key, access_token)

# Dictionary to store the latest prices
latest_prices = {}

def on_ticks(ws, ticks):
    for tick in ticks:
        instrument_token = tick['instrument_token']
        last_price = tick['last_price']
        print(f'Token : {instrument_token} price ; {last_price}')
        latest_prices[instrument_token] = last_price

def on_connect(ws, response):
    # Subscribe to multiple stocks by their instrument tokens
    ws.subscribe([738561, 5633, 424961])  # Example instrument tokens

def on_close(ws, code, reason):
    print("Closed connection on: {} - {}".format(code, reason))

def print_latest_prices():
    while True:
        time.sleep(1)  # Print prices every second
        # for token, price in latest_prices.items():
        #     print(f"Instrument Token: {token}, Last Price: {price}")

# Assign the callback functions
while True:
    kite_ticker.on_ticks = on_ticks
    kite_ticker.on_connect = on_connect
    kite_ticker.on_close = on_close

    # Start the WebSocket in a separate thread
    kite_ticker_thread = Thread(target=kite_ticker.connect)
    kite_ticker_thread.start()

    # Start printing prices in the main thread
    print_latest_prices()
