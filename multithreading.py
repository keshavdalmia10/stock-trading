import threading
import tickerDataHelper as tickerHelper
import datetime


def generate_all_charts_for_stock(stockname):
    startTime = datetime.datetime.now()
    # thread1 = threading.Thread(target=tickerHelper.trigger_5d_60min, args=(stockname,))
    thread2 = threading.Thread(target=tickerHelper.trigger_1d_15min, args=(stockname,))
    thread3 = threading.Thread(target=tickerHelper.trigger_1d_5min, args=(stockname,))

    # Start all three threads
    # thread1.start()
    thread2.start()
    thread3.start()

    # thread1.join()
    thread2.join()
    thread3.join()
    endTime = datetime.datetime.now()
    print(f'Images constructed in : {endTime - startTime}')
    print("All Image threads have finished.")


