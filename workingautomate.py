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
from ai_strategy import AIStrategy, AIStrategyConfig
import json
from datetime import datetime, timedelta
# from logging_config import LogLevel, set_logging_level
from stock import Stock
logger = logging.getLogger(__name__)

# set_logging_level(LogLevel.INFO)

#Credentials
api_key = "d2myrf8n2p720jby"
api_secret = "4l6bswdi9d5ti0dqki6kffoycgwpgla1"

#variables
THRESHOLD_PERCT = 1.5
MINIMUM_BALANCE = 1000
RATE_PER_STOCK = 8000
STOCK_CANCEL_DELAY = 10 #in seconds
AIStrategyConfig.set_strategy(AIStrategy.GENERATE_AND_USE_STOCKDATA) #set ai strategy


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

def round_to_nearest_0_05(value):
    return round(value * 20) / 20

def process_stock_cancel(tradingsymbol):
    time.sleep(STOCK_CANCEL_DELAY) 
    try:
        if tradingsymbol is not None:
            cancel_remaining_orders([tradingsymbol])
            print(f"Stock: {tradingsymbol} cancelled")
    except Exception as e:
        logger.warning(f"Error processing queue: {str(e)}")


def on_ticks(ws, ticks):
    for tick in ticks:
        last_price = tick['last_price']
        margin = math.floor(last_price / 5)
        instrumenttoken = tick['instrument_token']
        stock = instrument_stock_dic[instrumenttoken]
        stockname = stock.stock_name
        stocktradingStrategy = stock.trading_strategy
        tradablename = stockname.replace(".NS","")
        entry = stock.entry_point
        target = stock.target_point
        stoploss = stock.stop_loss
        target = round_to_nearest_0_05(target)
        stoploss = round_to_nearest_0_05(stoploss)
        if(stocktradingStrategy.lower() == "long"):
            if(last_price >= entry and is_within_threshold(entry_price=entry, latest_price=last_price, threshold_percentage=THRESHOLD_PERCT) and is_difference_not_greater_than(entry,last_price) and live_balance() - RATE_PER_STOCK >= MINIMUM_BALANCE):
                qty = math.floor(RATE_PER_STOCK / margin)
                print("\n")
                place_stock_order(qty, tradablename, kite.TRANSACTION_TYPE_BUY)
                place_stoploss(qty, stoploss, tradablename, kite.TRANSACTION_TYPE_SELL)
                place_target(qty,target, tradablename, kite.TRANSACTION_TYPE_SELL)
                handle_post_order_tasks(tradablename, instrumenttoken)
        elif(stocktradingStrategy.lower() == "short"):
            if(last_price <= entry and is_within_threshold(entry_price=entry, latest_price=last_price, threshold_percentage=THRESHOLD_PERCT) and is_difference_not_greater_than(entry,last_price) and live_balance() - RATE_PER_STOCK >= MINIMUM_BALANCE):
                qty = math.floor(RATE_PER_STOCK / margin)
                print("\n")
                place_stock_order(qty, tradablename, kite.TRANSACTION_TYPE_SELL)
                place_stoploss(qty, stoploss, tradablename, kite.TRANSACTION_TYPE_BUY)
                place_target(qty,target, tradablename, kite.TRANSACTION_TYPE_BUY)

                handle_post_order_tasks(tradablename, instrumenttoken)

        if showoutput:
            print(f'{tradablename}, entry: {entry}, currprice: {last_price}   diff(curr - entry): {last_price - entry}')

def handle_post_order_tasks(tradablename, instrumenttoken):
    removeNameFromSetInqeueu([tradablename])
    instruments_to_remove = [instrumenttoken]
    update_subscriptions(remove_tokens=instruments_to_remove)


def place_stock_order(quantity, tradingsymbol, transactionType):
    try:
        order_id = kite.place_order(tradingsymbol=tradingsymbol,
                                    variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    transaction_type=transactionType,
                                    quantity=quantity,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    product=kite.PRODUCT_MIS)
        print(f"Order placed for {tradingsymbol}")
        logger.info(f"Order placed for {tradingsymbol}")
        # logger.info(f"Order placed. ID is: {order_id}")
    except Exception as e:
        logger.warning(f"Purchase error for {tradingsymbol} : {str(e)}")

def cancel_remaining_orders(stocknamelist):
    orders = kite.orders()
    for stockname in stocknamelist:
        try:
            sl_orders = []
            limit_orders = []
            # Iterate through orders once and populate sl_orders and limit_orders
            for order in orders:
                # print(f"status : {order['status']} name: {order['tradingsymbol']} type: {order['order_type']}")
                if order['tradingsymbol'] == stockname:
                    if order['order_type'] == 'SL' and order['status'] == 'TRIGGER PENDING':
                        sl_orders.append(order)
                    elif order['order_type'] == 'LIMIT' and order['status'] == 'OPEN':
                        limit_orders.append(order)
            # print(f"Length sl: {len(sl_orders)}")
            # print(f"Length limit: {len(limit_orders)}")
            # Check if exactly one SL or one LIMIT order is present and cancel it
            if (len(sl_orders) == 1 and len(limit_orders) == 0) or (len(limit_orders) == 1 and len(sl_orders) == 0):
                order_to_cancel = sl_orders[0] if sl_orders else limit_orders[0]
                order_to_cancel_id = order_to_cancel['order_id']
                # print(f'Order to cancel : {order_to_cancel_id}')
                kite.cancel_order(order_id=order_to_cancel['order_id'], variety=order_to_cancel['variety'])
                logging.info(f"Cancelled order: {order_to_cancel['order_id']} for stock {order_to_cancel['tradingsymbol']}")

        except Exception as e:
            logging.error(f"Error cancelling orders: {e}")

def cancel_all_open_orders():
    orders = kite.orders()
    for stockorder in orders:
        order_id = stockorder['order_id']
        order_variety = stockorder['variety']
        order_stock_name = stockorder['tradingsymbol'] 
        status = stockorder['status']
        if(status == 'TRIGGER PENDING' or status == 'OPEN'):
            print(f'name: {order_stock_name} order id : {order_id} variety: {order_variety}')
            kite.cancel_order(order_id=order_id, variety=order_variety)

def place_stoploss(quantity, stoploss_price, tradingsymbol, transactionType):
        try: 
            stoploss_order_id = kite.place_order(
            tradingsymbol=tradingsymbol,
            exchange=kite.EXCHANGE_NSE,
            transaction_type=transactionType,
            quantity=quantity,
            order_type=kite.ORDER_TYPE_SL,
            price=stoploss_price,
            trigger_price=stoploss_price,
            product=kite.PRODUCT_MIS,
            variety=kite.VARIETY_REGULAR
    )
            print(f"Stoploss placed for {tradingsymbol} at {stoploss_price}")
            logger.info(f"Stoploss placed for {tradingsymbol} at {stoploss_price}")
        except Exception as e:
            logger.warning(f"Stoploss placing error for {tradingsymbol} : {str(e)}")

def place_target(quantity, target_price, tradingsymbol, transactionType):
        try: 
            target_order_id = kite.place_order(
            tradingsymbol=tradingsymbol,
            exchange=kite.EXCHANGE_NSE,
            transaction_type=transactionType,
            quantity=quantity,
            order_type=kite.ORDER_TYPE_LIMIT,
            price=target_price,
            product=kite.PRODUCT_MIS,
            variety=kite.VARIETY_REGULAR
    )
            print(f"Target placed for {tradingsymbol} at {target_price}")
            logger.info(f"Target placed for {tradingsymbol} at {target_price}")
        except Exception as e:
            logger.warning(f"Target placing error for {tradingsymbol} : {str(e)}")

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
        if oder_type == 'LIMIT' and order_transactin_type == 'SELL' and order_status == 'COMPLETE':
            print(f"Will cancel : {tradingsymbol} in {STOCK_CANCEL_DELAY} secs")
            cancel_thread = threading.Thread(target=process_stock_cancel, args=(tradingsymbol,))
            cancel_thread.daemon = True  # Daemonize thread
            cancel_thread.start()
        if oder_type == 'LIMIT' and order_transactin_type == 'BUY' and order_status == 'COMPLETE':
            # print(f"Manually cancel : {tradingsymbol}")
            cancel_thread = threading.Thread(target=process_stock_cancel, args=(tradingsymbol,))
            cancel_thread.daemon = True  # Daemonize thread
            cancel_thread.start()
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

def mapInstrumentTokens(stockobjectlist : List[Stock]):
    instrumentokenlistadded = []
    stocksetadd = set()
    for stock in stockobjectlist:
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
    
def live_balance():
    margins = kite.margins(segment="equity")
    live_balance = margins['available']['live_balance']
    return live_balance

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
            input_str = input("Enter instrument tokens to add (comma-separated) or 'exit' to quit: ")
            if input_str.lower().startswith("exit "):
                print("Exiting...")
                subscription_queue.put(None)
                kws.stop()
                break

            elif input_str.lower().startswith("add "):
                tokens_to_add = [item.strip().upper() for item in input_str[3:].split(',')]
                print(f'Tokens to add :{tokens_to_add}')
                stockobjectlist = trader.populateStockNamesWithAI(tokens_to_add)
                print(f'Trade stock size : {len(stockobjectlist)}')
                if len(stockobjectlist) >= 1:
                    instruements_to_add = mapInstrumentTokens(stockobjectlist)
                    update_subscriptions(add_tokens=instruements_to_add)

            elif input_str.lower().startswith("rem "):
                stocknames_to_remove = [item.strip().upper() for item in input_str[3:].split(',')]
                filtered_stocksname_inqueue = [s for s in stocknames_to_remove if s in stocksetInQueue]
                if len(filtered_stocksname_inqueue) >= 1:
                    removeNameFromSetInqeueu(filtered_stocksname_inqueue)
                    instruments_to_remove = [fetch_instrument_token(stockname) for stockname in filtered_stocksname_inqueue]    
                    update_subscriptions(remove_tokens=instruments_to_remove)
                    print(f'Removed : {filtered_stocksname_inqueue}.')
                print(stocksetInQueue)

            elif input_str.lower().startswith("queue"):
                print(stocksetInQueue)

            elif input_str.lower().startswith("balance"):
                balance = live_balance()
                print(f'balance : {balance}')

            elif input_str.lower().startswith("output"):
                toggleoutput()

            elif input_str.lower().startswith("cancel "):
                token_to_cancel = [item.strip().upper() for item in input_str[6:].split(',')]
                print(f'Cancelling : {token_to_cancel}')
                cancel_remaining_orders(token_to_cancel)

            elif input_str.lower().startswith("clear queue"):
                 stocks_in_queue = [s for s in stocksetInQueue]
                 if len(stocks_in_queue) >= 1:
                    removeNameFromSetInqeueu(stocks_in_queue)
                    instruments_to_remove = [fetch_instrument_token(stockname) for stockname in stocks_in_queue]    
                    update_subscriptions(remove_tokens=instruments_to_remove)
                    print(f'QUEUE CLEARED')
                 else:
                     print("Queue is already empty")

            elif input_str.lower().startswith("exit all"):
                    cancel_all_open_orders()
                    exit_all_positions()
                
        except ValueError:
            print("Invalid input. Please enter comma-separated instrument tokens.")

def exit_all_positions():
    positions = kite.positions()
    if positions:
        position_stocks = [position for position in positions['day'] if position['quantity'] != 0]
        if position_stocks:
            for stock in position_stocks:
                stockExitName = stock['tradingsymbol']
                stockExitQty = stock['quantity']
                stockExitTransaction = kite.TRANSACTION_TYPE_SELL if stockExitQty > 0 else kite.TRANSACTION_TYPE_BUY
                                # print(stockExitName)
                                # print(stockExitQty)
                                # print(stockExitTransaction)
                place_stock_order(abs(stockExitQty), stockExitName, stockExitTransaction)

        else:
            print("No stocks in positions.")
    else:
        print("Failed to retrieve positions.")

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
