import signal
import sys
import threading
from queue import Queue
from typing import List, Dict
from kiteconnect import KiteTicker, KiteConnect
import logging
import trader as trader
import math
from stock import Stock
logger = logging.getLogger(__name__)

#Credentials
api_key = "d2myrf8n2p720jby"
api_secret = "4l6bswdi9d5ti0dqki6kffoycgwpgla1"
access_token = "iEbXRbBNhWeXaQNGCTwtgchaf0v06nmN"

# Initialize KiteTicker object
kws = KiteTicker(api_key, access_token)
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# Queue to handle subscription changes
subscription_queue = Queue()
stocksetInQueue = set()
instrument_stock_dic = {}

showoutput = False


def on_ticks(ws, ticks):
    for tick in ticks:
        last_price = tick['last_price']
        margin = math.floor(last_price / 5)
        instrumenttoken = tick['instrument_token']
        stock = instrument_stock_dic[instrumenttoken]
        stockname = stock.stock_name
        tradablename = stockname.replace(".NS","")
        entry = stock.entry_point
        target = stock.target_point
        stoploss = stock.stop_loss
        entry = math.floor(entry * 10) / 10
        target = math.floor(target * 10) / 10
        stoploss = math.floor(stoploss * 10) / 10
        if(last_price >= entry and last_price - entry <= 1.5 and last_price - entry >= 0 and live_balance() - 5000 >= 5000):
            qty = math.floor(5000 / margin)
            place_stock_order(qty, tradablename)
            place_stoploss(qty, stoploss, tradablename)
            place_target(qty,target, tradablename)

            removeNameFromSetInqeueu([tradablename])
            instruments_to_remove = [instrumenttoken]    
            update_subscriptions(remove_tokens=instruments_to_remove)

        # print(f"Instrument Token: {tick['instrument_token']}, Last Price: {tick['last_price']}")
        if showoutput:
            print(f'{tradablename}, entry: {entry}, currprice: {last_price}')

def place_stock_order(quantity, tradingsymbol):
    try:
        order_id = kite.place_order(tradingsymbol=tradingsymbol,
                                    variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NSE,
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=quantity,
                                    order_type=kite.ORDER_TYPE_MARKET,
                                    product=kite.PRODUCT_MIS)
        print(f"Order placed for {tradingsymbol}")
        logger.info(f"Order placed for {tradingsymbol}")
        # logger.info(f"Order placed. ID is: {order_id}")
    except Exception as e:
        logger.warning(f"Purchase error for {tradingsymbol} : {str(e)}")

def place_stoploss(quantity, stoploss_price, tradingsymbol):
        try: 
            stoploss_order_id = kite.place_order(
            tradingsymbol=tradingsymbol,
            exchange=kite.EXCHANGE_NSE,
            transaction_type=kite.TRANSACTION_TYPE_SELL,
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

def place_target(quantity, target_price, tradingsymbol):
        try: 
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

# def on_order_update(ws, data):
#     print(f"Order update")

def fetch_instrument_token(tradingsymbol):
    try:
        instruments = kite.instruments(exchange="NSE")
        for instrument in instruments:
            if instrument['tradingsymbol'] == tradingsymbol:
                print(f"Found {tradingsymbol}: Token = {instrument['instrument_token']}, Name = {instrument['name']}")
                return instrument['instrument_token']
    except Exception as e:
        print(f"Failed to fetch instruments: {str(e)}")
    return None

def toggleoutput():
    originalbool = showoutput
    togglebool = False
    if originalbool:
        togglebool = False
    else:
        togglebool = True
    showoutput = togglebool

def mapInstrumentTokens(stockobjectlist : List[Stock]):
    instrumentokenlistadded = []
    stocksetadd = set()
    for stock in stockobjectlist:
        stockName = stock.stock_name
        tradableStockname = stockName.replace(".NS","")
        inst_token = fetch_instrument_token(tradableStockname)
        print(f'instuement token :{inst_token}')
        stock.intrtoken = inst_token
        instrumentokenlistadded.append(inst_token)
        instrument_stock_dic[inst_token] = stock
        stocksetadd.add(tradableStockname)
        print(f'Stock : {stock.stock_name} token={inst_token}')
    
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
# kws.on_order_update = on_order_update

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
            string_split = input_str.split()
            command = string_split[0].lower()
            if command == 'exit':
                print("Exiting...")
                subscription_queue.put(None)
                kws.stop()
                break
            elif command == 'add':
                tokens_to_add = [token.strip() for token in string_split[1].split(",")]
                print(f'Tokens to add :{tokens_to_add}')
                stockobjectlist = trader.get_tradable_stocklist(tokens_to_add)
                print(f'Trade stock size : {len(stockobjectlist)}')
                if len(stockobjectlist) >= 1:
                    instruements_to_add = mapInstrumentTokens(stockobjectlist)
                    update_subscriptions(add_tokens=instruements_to_add)
            elif command == 'rem':
                stocknames_to_remove = [token.strip() for token in string_split[1].split(",")]
                filtered_stocksname_inqueue = [s for s in stocknames_to_remove if s in stocksetInQueue]
                if len(filtered_stocksname_inqueue) >= 1:
                    removeNameFromSetInqeueu(filtered_stocksname_inqueue)
                    instruments_to_remove = [fetch_instrument_token(stockname) for stockname in filtered_stocksname_inqueue]    
                    update_subscriptions(remove_tokens=instruments_to_remove)
            elif command == 'queue':
                print(stocksetInQueue)
            elif command == 'balance':
                balance = live_balance()
                print(f'balance : {balance}')
            elif command == 'output':
                toggleoutput()
                
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
