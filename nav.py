from selenium.common.exceptions import NoSuchElementException

def click(driver, elements, element_id):
    # Find the element with the given ID
    target_element = None
    for element in elements:
        if element.get('id') == element_id:
            target_element = element['element']
            break

    if target_element is None:
        print(f"No element found with ID {element_id}")
        return
    
    target_outer_html = target_element.get_attribute('outerHTML')

    # Try to click on the element
    try:
        target_element.click()
    except NoSuchElementException:
        print(f"Element with ID {element_id} is not clickable or not found.")

    return target_outer_html, driver.current_url

def type(driver, elements, element_id, text_to_type):
    # Find the element with the given ID
    target_element = None
    for element in elements:
        if element.get('id') == element_id:
            target_element = element['element']
            break

    if target_element is None:
        print(f"No element found with ID {element_id}")
        return
    
    target_outer_html = target_element.get_attribute('outerHTML')

    # Try to type into the element
    try:
        target_element.clear()  # Clear the field before typing, if needed
        target_element.send_keys(text_to_type)
    except NoSuchElementException:
        print(f"Element with ID {element_id} not found or is not typeable.")

    return target_outer_html, driver.current_url

## IMPLEMENT SCROLL
