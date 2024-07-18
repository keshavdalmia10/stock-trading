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
access_token = "J8fOW6E0ZQwtYzDJ4cplJMCtiSC9QIei"

# Initialize KiteTicker object
kws = KiteTicker(api_key, access_token)
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# Queue to handle subscription changes
subscription_queue = Queue()
stocksetInQueue = set()
instrument_stock_dic = {}

showoutput = False

def is_within_threshold(entry_price, latest_price, threshold_percentage):
    threshold_value =entry_price * (threshold_percentage / 100.0)
    lower_bound = entry_price - threshold_value
    upper_bound = entry_price + threshold_value

    return lower_bound <= latest_price <= upper_bound

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
        target = math.floor(target * 10) / 10
        stoploss = math.floor(stoploss * 10) / 10
        if(last_price >= entry and is_within_threshold(entry_price=entry, latest_price=last_price, threshold_percentage=1.5) and live_balance() - 5000 >= 4000):
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

# def cancel_stock_order(order_id):
#     try:
#         kite.cancel_order(order_id=order_id,
#                           variety=kite.VARIETY_REGULAR)
#         print(f"Order {order_id} cancelled successfully")
#         logger.info(f"Order {order_id} cancelled successfully")
#     except Exception as e:
#         logger.warning(f"Cancellation error for order {order_id}: {str(e)}")

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
            print(f"Length sl: {len(sl_orders)}")
            print(f"Length limit: {len(limit_orders)}")
            # Check if exactly one SL or one LIMIT order is present and cancel it
            if (len(sl_orders) == 1 and len(limit_orders) == 0) or (len(limit_orders) == 1 and len(sl_orders) == 0):
                order_to_cancel = sl_orders[0] if sl_orders else limit_orders[0]
                order_to_cancel_id = order_to_cancel['order_id']
                print(f'Order to cancel : {order_to_cancel_id}')
                kite.cancel_order(order_id=order_to_cancel['order_id'], variety=order_to_cancel['variety'])
                logging.info(f"Cancelled order: {order_to_cancel['order_id']} for stock {order_to_cancel['tradingsymbol']}")

        except Exception as e:
            logging.error(f"Error cancelling orders: {e}")


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

def on_order_update(ws, data):
    try:
        order_id = data['order_id']
        status = data['status']
        tradingsymbol = data['tradingsymbol']
        # if status in ['COMPLETE', 'TRIGGERED']:
        # print(f"Stock {data['tradingsymbol']} ordertype: {data['order_type']} transactiontype: {data['transaction_type']}. status: {data['status']} orderid: {data['order_id']}")
        if data['order_type'] == 'LIMIT' and data['transaction_type'] == 'SELL' and data['status'] == 'COMPLETE':
            print(f"Should cancel : {data['tradingsymbol']}")
    except Exception as e:
        print((f"Error in on_order_update callback for order {order_id} ({tradingsymbol}): {str(e)}"))
        logger.warning(f"Error in on_order_update callback for order {order_id} ({tradingsymbol}): {str(e)}")

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
            elif command == 'cancel':
                token_to_cancel = [token.strip() for token in string_split[1].split(",")]
                cancel_remaining_orders(token_to_cancel)
                
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
