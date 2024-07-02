import requests
import os

generate_chart_url = "http://localhost:3000/generate-chart"
fibonaci_classic_url = "https://stock-trading-flask-13fc31362bcf.herokuapp.com/api/pivot"
stock_data_url = "https://stock-trading-flask-13fc31362bcf.herokuapp.com/api/data"
# fibonaci_classic_url = "http://127.0.0.1:8000/api/pivot"
# stock_data_url = "http://127.0.0.1:8000/api/data"

def constructTickerImages(symbol, timeframe, interval) -> bool:
    url = f"{generate_chart_url}/{symbol}/{timeframe}/{interval}"
    response = requests.get(url)
    if response.status_code == 200:
        print("Response received successfully!")
        return True
    else:
        print(f"Failed to get image for {symbol} {timeframe} {interval} for  response. Status code: {response.status_code}")
        return False
    
def get_stock_data(symbol, timeframe, interval):
    url = f"{stock_data_url}/{symbol}/{timeframe}/{interval}" 
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()


def get_Classic_Fibonacci(symbol, timeframe, interval):
    url = f"{fibonaci_classic_url}/{symbol}/{timeframe}/{interval}"
    response = requests.get(url)
    if response.status_code == 200:
        print("Response received successfully!")
        return response.json()
    else:
        print(f"Failed to get fibonacci response. Status code: {response.status_code}")

def trigger_1d_5min(stockname):
    interval = "5m"
    timeperiod = "1d"
    deleteImageIfExist(stockname, interval)
    image_generated = constructTickerImages(symbol=stockname, timeframe=timeperiod, interval=interval)
    
    if(image_generated):
        print(f"Images succesfully generated for {interval}")
    else:
        print(f"Images didn't generate for {timeperiod} {interval}")


def trigger_5d_15min(stockname):
    interval = "15m"
    timeperiod = "5d"
    deleteImageIfExist(stockname, "15m")
    image_generated = constructTickerImages(symbol=stockname, timeframe=timeperiod, interval=interval)
    
    if(image_generated):
        print(f"Images succesfully generated for {interval}")
    else:
        print(f"Images didn't generate for {timeperiod} {interval}")

def trigger_1d_15min(stockname):
    interval = "15m"
    timeperiod = "1d"
    deleteImageIfExist(stockname, "15m")
    image_generated = constructTickerImages(symbol=stockname, timeframe=timeperiod, interval=interval)
    
    if(image_generated):
        print(f"Images succesfully generated for {interval}")
    else:
        print(f"Images didn't generate for {timeperiod} {interval}")


def trigger_5d_60min(stockname):
    interval = "60m"
    timeperiod = "5d"
    deleteImageIfExist(stockname, "60m")
    image_generated = constructTickerImages(symbol=stockname, timeframe=timeperiod, interval=interval)
    
    if(image_generated):
        print(f"Images succesfully generated for {interval}")
    else:
        print(f"Images didn't generate for {timeperiod} {interval}")

def getTickerImagePath(stockname, interval):
    image_file_name = f'{stockname}-{interval}-chart.png'
    image_file_path = f'my-stock-app/{image_file_name}'
    if os.path.exists(image_file_path):
        return image_file_path
    else:
        return f'ERROR: Image file path {image_file_path} does not exist'
    
def deleteImageIfExist(stockname, interval):
    image_file_name = f'{stockname}-{interval}-chart.png'
    image_file_path = f'my-stock-app/{image_file_name}'
    if os.path.exists(image_file_path):
        os.remove(image_file_path)

def delete_all_generated_images(stockname):
    deleteImageIfExist(stockname, "60m")
    deleteImageIfExist(stockname, "5m")
    deleteImageIfExist(stockname, "15m")