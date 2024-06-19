import yfinance as yf
import mplfinance as mpf
import numpy as np
import pandas as pd

# Function to calculate RSI
def rsi(data, window):
    diff = data.diff(1).dropna()
    gain = (diff.where(diff > 0, 0)).fillna(0)
    loss = (-diff.where(diff < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Function to calculate ATR
def atr(data, window):
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(window=window).mean()

# Function to calculate MACD and MACD Signal
def macd(data, fast_period, slow_period, signal_period):
    exp1 = data['Close'].ewm(span=fast_period, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow_period, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    return macd_line, signal_line

# Fetch historical data for Apple (ticker symbol 'AAPL')
data = yf.download('AAPL', start='2023-01-01', end='2023-06-01')

# Create weights for WMA
weights = np.arange(1, 21)

# Calculate SMA, WMA, EMA
sma = data['Close'].rolling(window=20).mean()
wma = data['Close'].rolling(20).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)
ema = data['Close'].ewm(span=20, adjust=False).mean()

# Calculate RSI
rsi_values = rsi(data['Close'], 14)

# Calculate ATR
atr_values = atr(data, 14)

# Calculate MACD and Signal
macd_line, signal_line = macd(data, 12, 26, 9)

# Align data for plotting
valid_index = max(sma.first_valid_index(), wma.first_valid_index(), ema.first_valid_index(), rsi_values.first_valid_index(), atr_values.first_valid_index(), macd_line.first_valid_index(), signal_line.first_valid_index())
sma = sma.loc[valid_index:]
wma = wma.loc[valid_index:]
ema = ema.loc[valid_index:]
rsi_values = rsi_values.loc[valid_index:]
atr_values = atr_values.loc[valid_index:]
macd_line = macd_line.loc[valid_index:]
signal_line = signal_line.loc[valid_index:]
data = data.loc[valid_index:]

# Customize market colors and style
mc = mpf.make_marketcolors(up='green', down='red', inherit=True)
s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc)

# Plot configuration and save the image
mpf.plot(data, type='candle', style=s, volume=True,
         addplot=[mpf.make_addplot(sma, color='blue'),
                  mpf.make_addplot(wma, color='green'),
                  mpf.make_addplot(ema, color='red'),
                  mpf.make_addplot(rsi_values, panel=2, color='purple', ylabel='RSI (14)'),
                  mpf.make_addplot(atr_values, panel=3, color='orange', ylabel='ATR (14)'),
                  mpf.make_addplot(macd_line, panel=4, color='blue', ylabel='MACD'),
                  mpf.make_addplot(signal_line, panel=4, color='red')],
         title='AAPL Chart with Volume, SMA, WMA, EMA, RSI, ATR, and MACD', ylabel='Price ($)',
         panel_ratios=(4, 1, 1, 1, 1), figratio=(18, 10), figscale=1.2,
         savefig='AAPL_Chart.png')
