from kiteconnect import KiteConnect
import os
import json
from datetime import datetime, timedelta

# Define your API key and secret
api_key = "d2myrf8n2p720jby"
api_secret = "4l6bswdi9d5ti0dqki6kffoycgwpgla1"

session_file = "kite_session.json"

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def save_session(data):
    # Convert all datetime objects to strings before saving
    data = json.dumps(data, default=datetime_handler)
    with open(session_file, "w") as file:
        file.write(data)

def load_session():
    if os.path.exists(session_file):
        with open(session_file, "r") as file:
            data = json.load(file)
            if 'expiry' in data:
                data['expiry'] = datetime.fromisoformat(data['expiry'])
            return data
    return None

# Initialize KiteConnect client
kite = KiteConnect(api_key=api_key)

# Try to load the existing access token
session_data = load_session()
if session_data and session_data.get("access_token") and (session_data.get("expiry") and session_data.get("expiry") > datetime.now()):
    kite.set_access_token(session_data["access_token"])
    print("Using saved access token.")
else:
    print("No valid session found, require login.")
    print("Visit this URL to login:", kite.login_url())
    request_token = input("Enter the request token: ")
    data = kite.generate_session(request_token, api_secret=api_secret)
    kite.set_access_token(data["access_token"])
    # Update data with expiry
    data['expiry'] = datetime.now() + timedelta(days=1)
    save_session(data)


c=0

# Fetch all instruments
try:
    instruments = kite.instruments()
    # Filter for a specific stock by its trading symbol and exchange
    for instrument in instruments:
        if instrument['tradingsymbol'] == 'INFY' and instrument['exchange'] == 'NSE':
            c+=1
            print(f"Found Infosys: Token = {instrument['instrument_token']}, Name = {instrument['name']}")
    print(c)
except Exception as e:
    print(f"Failed to fetch instruments: {str(e)}")