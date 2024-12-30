from kiteconnect import KiteConnect, KiteTicker
import threading

# Define your API key and secret
api_key = "d2myrf8n2p720jby"
api_secret = "4l6bswdi9d5ti0dqki6kffoycgwpgla1"

# Initialize KiteConnect client
kite = KiteConnect(api_key=api_key)

# Generate the login URL to obtain the request token
print("Visit this URL to login:", kite.login_url())

# Input request token obtained from redirect URL
request_token = input("Enter the request token: ")

# Generate session to get access token
data = kite.generate_session(request_token, api_secret=api_secret)
kite.set_access_token(data["access_token"])
access_token = data["access_token"]

# Define the stock and trading parameters
while(True):
    entry_price = float(input("Enter the entry price: "))
    instrument_token = 408065  # Example token for Infosys; replace with your stock's token

    # Function to place an order
    def place_order():
        try:
            order_id = kite.place_order(tradingsymbol="INFY",
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
        if current_price <= entry_price:
            print("Target price reached, placing order...")
            place_order()
            ws.close()

    def on_connect(ws, response):
        ws.subscribe([instrument_token])
        ws.set_mode(ws.MODE_FULL, [instrument_token])

    def on_close(ws, code, reason):
        print(f"WebSocket closed: {code} | {reason}")

    # Starting the KiteTicker to get live market data
    kws = KiteTicker(api_key, access_token)

    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close

    # Start the WebSocket in a new thread
    thread = threading.Thread(target=kws.connect)
    thread.start()


