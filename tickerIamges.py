import requests

base_url = "http://localhost:3000/generate-chart"

def constructTickerImages(symbol, timeframe, interval):
    url = f"{base_url}/{symbol}/{timeframe}/{interval}"
    response = requests.get(url)
    if response.status_code == 200:
        print("Response received successfully!")
        return True
    else:
        print(f"Failed to get response. Status code: {response.status_code}")
        return False



