import threading
import tickerDataHelper as tickerHelper


def generate_all_charts_for_stock(stockname):
    thread1 = threading.Thread(target=tickerHelper.trigger_5d_60min, args=(stockname,))
    thread2 = threading.Thread(target=tickerHelper.trigger_1d_15min, args=(stockname,))
    thread3 = threading.Thread(target=tickerHelper.trigger_1d_5min, args=(stockname,))

    # Start all three threads
    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

print("All threads have finished.")


