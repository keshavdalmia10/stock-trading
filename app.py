from flask import Flask, jsonify
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def fetch_stock_data(ticker):
    # Downloading the stock data using yfinance with a daily interval
    data = yf.download(tickers=ticker, period="5d", interval="15m")
    data.reset_index(inplace=True)
    
    # Check if 'Date' column is present, rename it to 'Datetime' if so
    if 'Date' in data.columns:
        data.rename(columns={'Date': 'Datetime'}, inplace=True)
        data['Datetime'] = data['Datetime'].dt.strftime('%Y-%m-%d')
    
    # Including volume in the formatted data
    formatted_data = data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='records')
    return formatted_data

@app.route('/api/data/<ticker>')
def get_data(ticker):
    # Fetching stock data
    stock_data = fetch_stock_data(ticker)
    # Returning JSON response
    return jsonify(stock_data)

if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(debug=True, port=5000)
