import signal
import sys
import threading
from queue import Queue
from typing import List, Dict
from kiteconnect import KiteTicker, KiteConnect
import logging
import trader as trader
import math
import time
import os
import json
from trailing_stock import TrailingStock
from datetime import datetime, timedelta
# from logging_config import LogLevel, set_logging_level
from stock import Stock
logger = logging.getLogger(__name__)

# set_logging_level(LogLevel.INFO)

#Credentials
api_key = "d2myrf8n2p720jby"
api_secret = "4l6bswdi9d5ti0dqki6kffoycgwpgla1"

#variables
STOCK_CANCEL_DELAY = 5 #in seconds#set ai strategy


# Queue to handle subscription changes
subscription_queue = Queue()
stocksetInQueue = set()
instrument_stock_dic = {}

showoutput = False

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


# Initialize KiteTicker object

kite = KiteConnect(api_key=api_key)
session_data = load_session()
access_token = ""
if session_data and session_data.get("access_token") and (session_data.get("expiry") and session_data.get("expiry") > datetime.now()):
    kite.set_access_token(session_data["access_token"])
    access_token = session_data["access_token"]
    print("Using saved access token.")
else:
    print("No valid session found, require login.")
    print("Visit this URL to login:", kite.login_url())
    request_token = input("Enter the request token: ")
    data = kite.generate_session(request_token, api_secret=api_secret)
    kite.set_access_token(data["access_token"])
    access_token = data["access_token"]
    # Update data with expiry
    data['expiry'] = datetime.now() + timedelta(days=1)
    save_session(data)

kws = KiteTicker(api_key, access_token)

def is_within_threshold(entry_price, latest_price, threshold_percentage):
    threshold_value =entry_price * (threshold_percentage / 100.0)
    lower_bound = entry_price - threshold_value
    upper_bound = entry_price + threshold_value

    return lower_bound <= latest_price <= upper_bound

def is_difference_not_greater_than(num1, num2):
    difference = abs(num1 - num2)
    
    if num1 <= 100:
        return difference <= 0.05
    elif num1 <= 500 and num1 > 100:
        return difference <= 0.2
    elif num1 <=1000 and num1 > 500:
        return difference <= 1
    else:
        return difference <= 1.25
    
def is_current_price_close_to_target(curr_price, target, strategy):
    if not is_difference_not_greater_than(curr_price, target):
        return False

    if strategy == "long":
        return curr_price < target
    elif strategy == "short":
        return curr_price > target
    else:
        raise ValueError(f"Invalid strategy: {strategy}")
    
def is_current_price_close_to_initialTarget(curr_price, initial_target, strategy):
    if strategy == "long":
        return curr_price >= initial_target
    elif strategy == "short":
        return curr_price <= initial_target
    else:
        raise ValueError(f"Invalid strategy: {strategy}")

def round_to_nearest_0_05(value):
    return round(value * 20) / 20

def add_trailing_stock(tradingsymbol):
    time.sleep(STOCK_CANCEL_DELAY) 
    try:
        if tradingsymbol is not None:
            addTrailingStockInQueue(tradingsymbol)
    except Exception as e:
        logger.warning(f"Error processing queue: {str(e)}")


def on_ticks(ws, ticks):
    for tick in ticks:
        last_price = tick['last_price']
        instrumenttoken = tick['instrument_token']
        stock = instrument_stock_dic[instrumenttoken]
        stockname = stock.stock_name
        target = stock.target_point
        stoploss = stock.stop_loss
        stock_strategy = stock.trading_strategy

        if not stock.target_removed and is_current_price_close_to_target(last_price, target, stock_strategy):
            diff = abs(target - stoploss)
            new_target = 0
            if(stock_strategy == "long"):
                new_target = target + (0.5 * diff)
            elif(stock_strategy == "short"):
                new_target = target - (0.5 * diff)
            rounded_target = round_to_nearest_0_05(new_target) 
            modify_target_order(stock.target_id, rounded_target)
            print(f'Target for {stockname} modified from {target} to {rounded_target}')
            stock.target_point = rounded_target
            stock.initial_target = target
            stock.target_removed = True
        
        elif stock.target_removed and is_current_price_close_to_initialTarget(last_price, stock.initial_target, stock_strategy):
            final_stoploss = 0
            if(stock_strategy == "long"):
                final_stoploss = stock.initial_target - 0.05
            elif(stock_strategy == "short"):
                final_stoploss = stock.initial_target + 0.05
            modify_stoploss_order(stock.stoploss_id, final_stoploss)
            print(f'Stoploss for {stockname} modified from {stoploss} to {stock.initial_target - 0.05}')
            stock.target_removed = False

        if showoutput:
            print(f'{stockname}, currprice: {last_price}')

def handle_post_order_tasks(tradablename, instrumenttoken):
    removeNameFromSetInqeueu([tradablename])
    instruments_to_remove = [instrumenttoken]
    update_subscriptions(remove_tokens=instruments_to_remove)


def modify_target_order(order_id, new_target_price):
    try:
        response = kite.modify_order(
            variety=kite.VARIETY_REGULAR,
            order_id=order_id,  
            price=new_target_price
        )
        # print("Target modification response:", response)
    except Exception as e:
        print("Error modifying target:", str(e))

def modify_stoploss_order(order_id, new_stoploss):
    try:
        response = kite.modify_order(
            variety=kite.VARIETY_REGULAR,
            order_id=order_id,              
            trigger_price=new_stoploss,     
            price=new_stoploss           
        )
        # print("Stoploss modification response:", response)
    except Exception as e:
        print("Error modifying Stoploss:", str(e))

def addTrailingStockInQueue(stockname):
    trailing_stock = TrailingStock(stockname)
    orders = kite.orders()
    for order in orders:
        if order['tradingsymbol'] == stockname:
            if order['order_type'] == 'SL' and order['status'] == 'TRIGGER PENDING':
                trailing_stock.stoploss_id = int(order['order_id'])
                trailing_stock.stop_loss = order['price']
            elif order['order_type'] == 'LIMIT' and order['status'] == 'OPEN':
                trailing_stock.target_id = int(order['order_id'])
                trailing_stock.target_point = order['price']

    if(trailing_stock.target_point > trailing_stock.stop_loss):
        trailing_stock.trading_strategy = "long"
    elif(trailing_stock.target_point < trailing_stock.stop_loss):
        trailing_stock.trading_strategy = "short"
    else:
        print(f'Stock {stockname} strategy assign error')
        return

    print(f'{trailing_stock.stock_name}  StoplossID:{trailing_stock.stoploss_id} stoploss_price:{trailing_stock.stop_loss}')
    print(f'{trailing_stock.stock_name}  TargetID:{trailing_stock.target_id} target_price:{trailing_stock.target_point}')
    print(f'{trailing_stock.stock_name} strategy: {trailing_stock.trading_strategy}')
    print()

    instruements_to_add = mapInstrumentTokens(trailing_stock)
    update_subscriptions(add_tokens=instruements_to_add)

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
    try:
        order_id = data['order_id']
        order_status = data['status']
        tradingsymbol = data['tradingsymbol']
        order_transactin_type = data['transaction_type']
        oder_type = data['order_type']
        if oder_type == 'MARKET' and (order_transactin_type == 'BUY' or order_transactin_type == 'SELL') and order_status == 'COMPLETE':
            add_stock_thread = threading.Thread(target=add_trailing_stock, args=(tradingsymbol,))
            add_stock_thread.daemon = True  # Daemonize thread
            add_stock_thread.start()

        elif oder_type == 'LIMIT' and (order_transactin_type == 'SELL' or order_transactin_type == 'BUY') and order_status == 'COMPLETE':
            print(f"Removed stock: {tradingsymbol} from queue")
            if tradingsymbol in stocksetInQueue:
                removeNameFromSetInqeueu([tradingsymbol])
                instruments_to_remove = [fetch_instrument_token(tradingsymbol)]    
                update_subscriptions(remove_tokens=instruments_to_remove)
            
    except Exception as e:
        print((f"Error in on_order_update callback for order {order_id} ({tradingsymbol}): {str(e)}"))
        logger.warning(f"Error in on_order_update callback for order {order_id} ({tradingsymbol}): {str(e)}")

def fetch_instrument_token(tradingsymbol):
    try:
        instruments = kite.instruments(exchange="NSE")
        for instrument in instruments:
            if instrument['tradingsymbol'] == tradingsymbol:
                # print(f"Found {tradingsymbol}: Token = {instrument['instrument_token']}, Name = {instrument['name']}")
                return instrument['instrument_token']
    except Exception as e:
        print(f"Failed to fetch instruments: {str(e)}")
    return None

def toggleoutput():
    global showoutput
    if showoutput:
        showoutput = False
    else:
        showoutput = True
    print(f"output is now : {showoutput}")

def mapInstrumentTokens(stock):
    instrumentokenlistadded = []
    stocksetadd = set()
    stockName = stock.stock_name
    tradableStockname = stockName.replace(".NS","")
    inst_token = fetch_instrument_token(tradableStockname)
    # print(f'instuement token :{inst_token}')
    stock.intrtoken = inst_token
    instrumentokenlistadded.append(inst_token)
    instrument_stock_dic[inst_token] = stock
    stocksetadd.add(tradableStockname)
    # print(f'Stock : {stock.stock_name} token={inst_token}')
    
    stocksetInQueue.update(stocksetadd)
    return instrumentokenlistadded 
    

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
            print("\n")
            input_str = input("TRAILING STRATEGY (only add one stock at a time): ")
            if input_str.lower().startswith("exit "):
                print("Exiting...")
                subscription_queue.put(None)
                kws.stop()
                break

            elif input_str.lower().startswith("add "):
                tokens_to_add = [item.strip().upper() for item in input_str[3:].split(',')]
                print(f'Tokens to add :{tokens_to_add}')
                if(len(tokens_to_add) == 1):
                    add_trailing_stock(tokens_to_add[0])

            elif input_str.lower().startswith("rem "):
                stocknames_to_remove = [item.strip().upper() for item in input_str[3:].split(',')]
                filtered_stocksname_inqueue = [s for s in stocknames_to_remove if s in stocksetInQueue]
                if len(filtered_stocksname_inqueue) >= 1:
                    removeNameFromSetInqeueu(filtered_stocksname_inqueue)
                    instruments_to_remove = [fetch_instrument_token(stockname) for stockname in filtered_stocksname_inqueue]    
                    update_subscriptions(remove_tokens=instruments_to_remove)

            elif input_str.lower().startswith("queue"):
                print(stocksetInQueue)

            elif input_str.lower().startswith("output"):
                toggleoutput()

            elif input_str.lower().startswith("clear queue"):
                 stocks_in_queue = [s for s in stocksetInQueue]
                 if len(stocks_in_queue) >= 1:
                    removeNameFromSetInqeueu(stocks_in_queue)
                    instruments_to_remove = [fetch_instrument_token(stockname) for stockname in stocks_in_queue]    
                    update_subscriptions(remove_tokens=instruments_to_remove)
                 else:
                     print("Queue is already empty")
                
        except ValueError:
            print("Invalid input. Please enter comma-separated instrument tokens.")

def removeNameFromSetInqeueu(filtered_stocksname_inqueue):
    for name in filtered_stocksname_inqueue:
        if name in stocksetInQueue:
            stocksetInQueue.remove(name)

# Start the user input loop in a separate thread
input_thread = threading.Thread(target=user_input_loop)
input_thread.daemon = True
input_thread.start()

# Keep the script running
stop_event = threading.Event()
stop_event.wait()
