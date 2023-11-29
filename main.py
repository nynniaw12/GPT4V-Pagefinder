from selenium import webdriver
from dotenv import load_dotenv
import json
import os
from window import screen_page
from chatgpt import vision_decide

load_dotenv()
openai_api_key = os.environ.get('OPENAI_API_KEY')

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

filtered_elems, l_path = screen_page(driver, url, data_directory, min_width, min_height)

print(vision_decide(openai_api_key, l_path, "Search").json())
print(vision_decide(openai_api_key, l_path, "Search", prev='"action": "click", "element": 8').json())
print(vision_decide(openai_api_key, l_path, "Search", prev='"action": "type", "element": 8, "text": ""').json())
print(vision_decide(openai_api_key, l_path, "Search", prev=' "action": "click", "element": 11 ').json())



driver.quit()