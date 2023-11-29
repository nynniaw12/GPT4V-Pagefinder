from selenium import webdriver
import os
from window import screen_page

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--hide-scrollbars')
driver = webdriver.Chrome(options=options)

min_width = 1920
min_height = 1080

url = 'https://www.google.com/'

current_directory = os.path.dirname(os.path.abspath(__file__))
data_directory = os.path.join(current_directory, 'data')

if not os.path.exists(data_directory):
    os.makedirs(data_directory)

screen_page(driver, url, data_directory, min_width, min_height)

driver.quit()