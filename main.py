from selenium import webdriver
from dotenv import load_dotenv
from window import screen_page
from chatgpt import vision_decide
from nav import click, type
from queue import Queue
import json
import os


################################
##############SETUP#############
################################
load_dotenv()
openai_api_key = os.environ.get('OPENAI_API_KEY')

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--hide-scrollbars')
driver = webdriver.Chrome(options=options)

min_width = 1920
min_height = 1080

cur_url = 'https://lepeep.com/'

current_directory = os.path.dirname(os.path.abspath(__file__))
data_directory = os.path.join(current_directory, 'data')

if not os.path.exists(data_directory):
    os.makedirs(data_directory)

done = False

driver.get(cur_url)




###############################
##############INIT#############
###############################
feature = "access menu"
nav_seq = Queue()
filtered_elems, l_path = screen_page(driver, data_directory, min_width, min_height)
response = vision_decide(openai_api_key, l_path, feature).json()

print("***Starting***")
while not done:
    prev = ""
    info = ""
    outer_html = None

    # Parse the JSON content inside the message
    message_content = response['choices'][0]['message']['content']
    message_content = message_content.replace('```json\n', '').replace('\n```', '')
    parsed_content = json.loads(message_content)
    brief_explanation = parsed_content['briefExplanation']
    next_action = parsed_content['nextAction']

    print("Brief Explanation:", brief_explanation)
    prev = next_action
    # print("Next Action:", next_action)

    if next_action['action'] == 'click':
        element_id = next_action['element']
        outer_html, next_url = click(driver, filtered_elems, element_id)
        print(f"Clicking on element with ID: {element_id}")
    elif next_action['action'] == 'type':
        element_id = next_action['element']
        text_to_type = next_action['text']  
        outer_html, next_url = type(driver, filtered_elems, element_id, text_to_type) 
        print(f"Typing '{text_to_type}' into element with ID: {element_id}")
    elif next_action['action'] == 'remember-info':
        info = next_action['info'] 
        print(f"Remembering {info} for the next cycle")
    elif next_action['action'] == 'done':
        done = True
        print("Done")
    else:
        print("Unknown action:", next_action['action'])


    if outer_html:
        nav_seq.put(outer_html)
    else:
        pass


    if cur_url != next_url:
        cur_url = next_url
        filtered_elems, l_path = screen_page(driver, data_directory, min_width, min_height)
    else:
        pass


    response = vision_decide(openai_api_key, l_path, feature, prev, info).json()


print("Navigation Sequence:")
while not nav_seq.empty():
    queued_outer_html = nav_seq.get()
    print(queued_outer_html)


driver.quit()

print("***Done***")