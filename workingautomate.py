import signal
import sys
import threading
from queue import Queue
from kiteconnect import KiteTicker
import logging

logging.basicConfig(level=logging.DEBUG)

# You need to have these credentials from your Kite account
api_key = "d2myrf8n2p720jby"
api_secret = "4l6bswdi9d5ti0dqki6kffoycgwpgla1"
access_token = "bJ7D05w8r6SMGvA9zA7wMqZAfjnMLAWw"

# Initialize KiteTicker object
kws = KiteTicker(api_key, access_token)

# Queue to handle subscription changes
subscription_queue = Queue()

def on_ticks(ws, ticks):
    for tick in ticks:
        print(f"Instrument Token: {tick['instrument_token']}, Last Price: {tick['last_price']}")

def on_connect(ws, response):
    print("Connected successfully!")
    # Initially subscribe to an empty list or some default instruments
    ws.subscribe([])

def on_close(ws, code, reason):
    print(f"Connection closed: {code} - {reason}")
    ws.stop()

def on_error(ws, code, reason):
    print(f"Error: {code} - {reason}")

def on_noreconnect(ws):
    print("No reconnect")

def on_reconnect(ws, attempts_count):
    print(f"Reconnect attempt: {attempts_count}")

def on_order_update(ws, data):
    print(f"Order update: {data}")

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

# Assign the callback functions
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.on_error = on_error
kws.on_noreconnect = on_noreconnect
kws.on_reconnect = on_reconnect
kws.on_order_update = on_order_update

# Function to handle subscription changes
def subscription_manager():
    current_subscriptions = set()
    while True:
        new_subscription = subscription_queue.get()
        if new_subscription is None:
            break
        add_tokens, remove_tokens = new_subscription
        if remove_tokens:
            kws.unsubscribe(list(remove_tokens))
            current_subscriptions -= remove_tokens
        if add_tokens:
            kws.subscribe(list(add_tokens))
            current_subscriptions |= add_tokens
        subscription_queue.task_done()

# Start the subscription manager thread
subscription_thread = threading.Thread(target=subscription_manager)
subscription_thread.daemon = True
subscription_thread.start()

# Function to add or remove subscriptions
def update_subscriptions(add_tokens=None, remove_tokens=None):
    add_tokens = set(add_tokens or [])
    remove_tokens = set(remove_tokens or [])
    subscription_queue.put((add_tokens, remove_tokens))

# Connect to WebSocket
kws.connect(threaded=True)

# Signal handler to gracefully shut down
def signal_handler(sig, frame):
    print("Interrupt received, stopping...")
    kws.stop()
    subscription_queue.put(None)
    sys.exit(0)

# Register signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Function to take input from the terminal and update subscriptions
def user_input_loop():
    while True:
        try:
            input_str = input("Enter instrument tokens to add (comma-separated) or 'exit' to quit: ")
            string_split = input_str.split()
            command = string_split[0].lower()
            if command == 'exit':
                print("Exiting...")
                subscription_queue.put(None)
                kws.stop()
                break
            elif command == 'add':
                tokens_to_add = [int(token.strip()) for token in string_split[1].split(",")]
                update_subscriptions(add_tokens=tokens_to_add)
            elif command == 'rem':
                tokens_to_remove = [int(token.strip()) for token in string_split[1].split(",")]
                update_subscriptions(remove_tokens=tokens_to_remove)
            # tokens_to_add = [int(token.strip()) for token in input_str.split(",")]
            # update_subscriptions(add_tokens=tokens_to_add)
        except ValueError:
            print("Invalid input. Please enter comma-separated instrument tokens.")

# Start the user input loop in a separate thread
input_thread = threading.Thread(target=user_input_loop)
input_thread.daemon = True
input_thread.start()

# Keep the script running
stop_event = threading.Event()
stop_event.wait()
