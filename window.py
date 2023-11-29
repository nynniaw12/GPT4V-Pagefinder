from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import os

def contrast_ratio(color1, color2):
    # Convert RGB values to relative luminance
    def luminance(color):
        r, g, b = color
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0
        r = r if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    # Calculate the contrast ratio
    luminance1 = luminance(color1)
    luminance2 = luminance(color2)
    if luminance1 > luminance2:
        return (luminance1 + 0.05) / (luminance2 + 0.05)
    else:
        return (luminance2 + 0.05) / (luminance1 + 0.05)
    

def get_random_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return (red, green, blue)

def element_contains(driver, parent: WebElement, child: WebElement):
    # Checks if the parent element contains the child element
    return driver.execute_script("return arguments[0].contains(arguments[1]);", parent, child)

def screen_page(driver, url, data_dir, min_width, min_height):
    driver.get(url)

    selector = "input, textarea, select, button, a, iframe, video"

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
    )

    required_width = driver.execute_script('return document.documentElement.scrollWidth')
    required_height = driver.execute_script('return document.documentElement.scrollHeight')

    if required_width < min_width:
        required_width = min_width

    if required_height < min_height:
        required_height = min_height

    driver.set_window_size(required_width, required_height)


    fp_path = os.path.join(data_dir, 'fp.png')


    all_elements = driver.find_elements(By.XPATH, "//*")

    extracted_elements = []

    for element in all_elements:
        try:
            if not element.is_displayed():
                continue

            tag_name = element.tag_name.upper()
            onclick = element.get_attribute("onclick")

            try:
                cursor_style = element.value_of_css_property("cursor")
            except Exception as e:
                cursor_style = None

            include = tag_name in ["INPUT", "TEXTAREA", "SELECT", "BUTTON", "A", "IFRAME", "VIDEO"] or \
                    onclick is not None or cursor_style == "pointer"

            rect = element.rect
            area = rect['width'] * rect['height']

            if include and area >= 200:
                text = ' '.join(element.text.split())  
                extracted_elements.append({
                    'element': element,
                    'area': area,
                    'rects': rect,
                    'text': text
                })

        except Exception as e:
            pass

    filtered_elements = []

    for e in extracted_elements:
        is_contained = False
        for other in extracted_elements:
            if e != other and element_contains(driver, other['element'], e['element']):
                is_contained = True
                break  
        
        if not is_contained:
            filtered_elements.append(e)


    # for element in filtered_elements:
    #     # Print element details
    #     print("Tag:", element['element'].tag_name)
    #     print("Text:", element['text'])
    #     print("Area:", element['area'])
    #     print("Rectangle:", element['rects'])
    #     print('-'*30)


    driver.save_screenshot(fp_path)

    # Load the screenshot
    screenshot = Image.open(fp_path)

    # if screenshot.mode != 'RGB':
    #     screenshot = screenshot.convert('RGB')

    draw = ImageDraw.Draw(screenshot)

    screen_width, screen_height = screenshot.size


    font_size = 32
    font = ImageFont.truetype("arialbd.ttf", font_size)

    # Assign IDs and extend filtered_elements with IDs
    for index, element in enumerate(filtered_elements):
        element['id'] = index + 1

    # Draw labels and bounding boxes on filtered elements
    for element in filtered_elements:
        rect = element['rects']
        # Generate a random color
        color = get_random_color()

        # Calculate contrast ratios
        contrast_with_white = contrast_ratio(color, (255, 255, 255))
        contrast_with_black = contrast_ratio(color, (0, 0, 0))
        
        # Determine the color for the box based on better contrast
        if contrast_with_white > contrast_with_black:
            box_color = "white"
        else:
            box_color = "black"
        
        
        text = str(element['id'])
        text_bbox = draw.textbbox((rect['x'], rect['y'] - 10), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        element_y = (rect['y'] + rect['y'] + rect['height']) / 2 
        
        if element_y <= screen_height / 2:
            # Element is in the upper half of the screen, draw at the bottom left
            box_x1 = rect['x'] - 2.5
            box_x2 = rect['x'] + text_width + 2.5
            box_y1 = rect['y'] + rect['height']
            box_y2 = box_y1 + text_height + 10
            text_position = (rect['x'], rect['y'] + rect['height'])
        else:
            # Element is in the lower half of the screen, draw at the top left
            box_x1 = rect['x'] - 2.5
            box_x2 = rect['x'] + text_width + 2.5
            box_y2 = rect['y'] 
            box_y1 = box_y2 - text_height - 10
            text_position = (rect['x'], rect['y'] - 32)

        # Draw a rectangle and text with the specified bold font and size
        draw.rectangle(
            [(rect['x'], rect['y']), (rect['x'] + rect['width'], rect['y'] + rect['height'])],
            outline=color,
            width=5
        )
        
        draw.rectangle([(box_x1, box_y1), (box_x2, box_y2)], fill=box_color)
        draw.text(text_position, str(element['id']), fill=color, font = font)


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"labeled_screenshot_{timestamp}.png"
    l_path = os.path.join(data_dir, filename)

    screenshot.save(l_path)

    return filtered_elements, l_path
