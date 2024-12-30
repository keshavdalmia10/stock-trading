import datetime as dt
import yfinance as yf
from lightweight_charts import Chart
import datetime

def set_bar_data(symbol, period, timeframe):
    chart = Chart(toolbox=False, debug=False)
    chart.legend(True)
    background_color_hex = "#f2eded"
    text_color_hex = "#000000"
    # comment below line to get light theme 
    # chart.layout(background_color=background_color_hex, text_color=text_color_hex)
    
    data = yf.download(tickers=symbol, period=period, interval=timeframe)

    if data.empty:
        return False
    chart.set(data)

    chart.topbar.textbox('symbol', symbol)
    chart.topbar.textbox('timeframe', timeframe)

    chart.show()  

    img = chart.screenshot()
    with open(f'screenshot_{symbol}_{timeframe}.png', 'wb') as f:
        f.write(img)
    print(f'Screenshot for {symbol} at {timeframe} saved.')

    chart.exit() 
    return True

def generate_all_charts(symbol):
    periods = ["1d"]
    timeframes = ["5m", "15m"]
    
    for period in periods:
        for timeframe in timeframes:
            set_bar_data(symbol, period, timeframe)

if __name__ == '__main__':
    symbol = "ZOMATO.NS"
    startTime = datetime.datetime.now()
    generate_all_charts(symbol)
    endTime = datetime.datetime.now()
    print(endTime - startTime)
