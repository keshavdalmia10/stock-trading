import threading
import time
from content import Content, ContentType
from message import Message, Role
from payload import Payload
from tickerDataHelper import trigger_1d_1min, trigger_1d_15min, trigger_1d_5min, getTickerImagePath
import os
from analyzable_stock import AnalyzableStock

# Create three threads, each calling a different method with "ZOMATO.NS" as argument
thread1 = threading.Thread(target=trigger_1d_1min, args=("RELIANCE.NS",))
thread2 = threading.Thread(target=trigger_1d_15min, args=("RELIANCE.NS",))
thread3 = threading.Thread(target=trigger_1d_5min, args=("RELIANCE.NS",))

# Start all three threads
thread1.start()
thread2.start()
thread3.start()

# Main thread continues here...
# You can do other work here while the threads are running

# Wait for all threads to complete (optional)
thread1.join()
thread2.join()
thread3.join()

# print("All threads have finished.")


# text_content = Content(content_type=ContentType.TEXT, value = "Analyze the json")
# f_content = Content(content_type=ContentType.TEXT, value = "Second")
# message = Message(role=Role.USER, content=[text_content,f_content])
# print(message)
# stock = AnalyzableStock("Zomato.NS")
# print(stock.message_history)
# stock.add_in_history(message)
# stock.add_in_history(message)
# stock.add_in_history(message)
# print(stock.message_history)

