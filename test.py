import threading
import time
from tickerDataHelper import trigger_1d_1min, trigger_1d_15min, trigger_1d_5min, getTickerImagePath


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


# trigger_1d_15min("RELIANCE.NS")
# trigger_1d_5min("RELIANCE.NS")

