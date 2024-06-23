from selenium import webdriver
import os
import time

# Set up the Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1200, 1100) 

# Path to your local HTML file
html_file_path = os.path.abspath(r'C:\Users\tanma\StockTradingAI\stock-trading\abc.html')
file_url = 'file:///' + html_file_path.replace('\\', '/')

# Open the HTML file
driver.get(file_url)
time.sleep(3)

# Take screenshot
screenshot_path = 'screenshot.png'
driver.save_screenshot(screenshot_path)

# Close the browser
driver.quit()

print(f"Screenshot saved to {screenshot_path}")
