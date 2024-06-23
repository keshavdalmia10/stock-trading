from flask import Flask, jsonify
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def fetch_stock_data(ticker, period, interval):
    data = yf.download(tickers=ticker, period=period, interval=interval)
    data.reset_index(inplace=True)
    if 'Date' in data.columns:
        data.rename(columns={'Date': 'Datetime'}, inplace=True)
    if 'Datetime' in data.columns:
        data['Datetime'] = data['Datetime'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    formatted_data = data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='records')
    return formatted_data

def calculate_pivot_points(data):
    high = data['High']
    low = data['Low']
    close = data['Close']

    P = (high + low + close) / 3
    R1 = 2 * P - low
    S1 = 2 * P - high
    R2 = P + (high - low)
    S2 = P - (high - low)
    R3 = high + 2 * (P - low)
    S3 = low - 2 * (high - P)

    fR1 = P + 0.382 * (high - low)
    fS1 = P - 0.382 * (high - low)
    fR2 = P + 0.618 * (high - low)
    fS2 = P - 0.618 * (high - low)
    fR3 = P + (high - low)
    fS3 = P - (high - low)

    return {
        "classic": {"P": P, "S1": S1, "S2": S2, "S3": S3, "R1": R1, "R2": R2, "R3": R3},
        "fibonacci": {"P": P, "S1": fS1, "S2": fS2, "S3": fS3, "R1": fR1, "R2": fR2, "R3": fR3}
    }

@app.route('/api/pivot/<ticker>/<period>/<interval>')
def get_pivot_data(ticker, period, interval):
    stock_data = fetch_stock_data(ticker, period, interval)
    if not stock_data:
        return jsonify({"error": "No data found"}), 404

    pivot_points = calculate_pivot_points(stock_data[-1])  
    pivot_response = {
        "interval": interval,
        "period": period,
        "pivot_points": {
            "classic": pivot_points['classic'],
            "fibonacci": pivot_points['fibonacci']
        }
    }
    return jsonify(pivot_response)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
