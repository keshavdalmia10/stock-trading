import yfinance as yf
import datetime
import os

# Set the stock ticker symbol
stock_symbol = "RELIANCE.NS"

# Create a directory for the stock if it doesn't exist
if not os.path.exists(stock_symbol):
    os.makedirs(stock_symbol)

# Set the start time to today's date at 9:30 AM and end time as now
start_time = datetime.datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
if datetime.datetime.now() < start_time:
    start_time = start_time - datetime.timedelta(days=1)
end_time = datetime.datetime.now()

# Fetch the data
data = yf.download(stock_symbol, start=start_time, end=end_time, interval='15m')

# Save the data to CSV
csv_file_path = f"{stock_symbol}/start_of_day_15min.csv"
data.to_csv(csv_file_path)
