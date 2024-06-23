import requests
import os

generate_chart_url = "http://localhost:3000/generate-chart"
fibonaci_classic_url = "http://127.0.0.1:8000/api/pivot"

def constructTickerImages(symbol, timeframe, interval) -> bool:
    url = f"{generate_chart_url}/{symbol}/{timeframe}/{interval}"
    response = requests.get(url)
    if response.status_code == 200:
        print("Response received successfully!")
        return True
    else:
        print(f"Failed to get response. Status code: {response.status_code}")
        return False
    
def get_Classic_Fibonacci(symbol, timeframe, interval):
    url = f"{fibonaci_classic_url}/{symbol}/{timeframe}/{interval}"
    response = requests.get(url)
    if response.status_code == 200:
        print("Response received successfully!")
        return response.json()
    else:
        print(f"Failed to get response. Status code: {response.status_code}")

def trigger_1d_5min(stockname):
    deleteImageIfExist(stockname, "5m")
    image_generated = constructTickerImages(symbol=stockname, timeframe="1d", interval="5m")
    
    if(image_generated):
        print("Images succesfully generated")
    else:
        print("Images didn't generate")


def trigger_1d_15min(stockname):
    deleteImageIfExist(stockname, "15m")
    image_generated = constructTickerImages(symbol=stockname, timeframe="1d", interval="15m")
    
    if(image_generated):
        print("Images succesfully generated")
    else:
        print("Images didn't generate")


def trigger_1d_1min(stockname):
    deleteImageIfExist(stockname, "1m")
    image_generated = constructTickerImages(symbol=stockname, timeframe="1d", interval="1m")
    
    if(image_generated):
        print("Images succesfully generated")
    else:
        print("Images didn't generate")

def getTickerImagePath(stockname, interval):
    image_file_name = f'{stockname}-{interval}-chart.png'
    image_file_path = f'my-stock-app/{image_file_name}'
    if os.path.exists(image_file_path):
        return image_file_path
    else:
        return f'ERROR: Image file path {image_file_path} does not exist'
    
def deleteImageIfExist(stockname, interval):
    image_file_name = f'{stockname}-{interval}chart.png'
    image_file_path = f'my-stock-app/{image_file_name}'
    if os.path.exists(image_file_path):
        os.remove(image_file_path)