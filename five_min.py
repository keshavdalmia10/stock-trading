import yfinance as yf
import datetime
import os

# Set the stock ticker symbol
stock_symbol = "RELIANCE.NS"

# Create a directory for the stock if it doesn't exist
if not os.path.exists(stock_symbol):
    os.makedirs(stock_symbol)

# Determine the end time as now and start time as 3 hours before
end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(hours=9)

# Fetch the data
data = yf.download(stock_symbol, start=start_time, end=end_time, interval='5m')

# Save the data to CSV
csv_file_path = f"{stock_symbol}/last_3_hours_5min.csv"
data.to_csv(csv_file_path)
