# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = 'product_'

@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert(message in context.driver.title)

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    assert(text_string not in element.text)

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)

@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)

@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = Select(context.driver.find_element(By.ID, element_id))
    assert(element.first_selected_option.text == text)

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = context.driver.find_element(By.ID, element_id)
    assert(element.get_attribute('value') == u'')

@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    assert(found)

@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)

######################################################################
# These functions are for button clicks
######################################################################

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element(By.ID, button_id).click()

    # For search operations, wait for the table to be updated
    if button.lower() == "search":
        import time
        time.sleep(2)  # Initial wait
        
        # Wait for table and contents
        table = WebDriverWait(context.driver, context.wait_seconds).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'table'))
        )
        
        # Wait for flash message to indicate search is complete
        element = WebDriverWait(context.driver, context.wait_seconds).until(
            expected_conditions.presence_of_element_located((By.ID, 'flash_message'))
        )
        
        # Get table contents for debugging
        rows = table.find_elements(By.TAG_NAME, 'tr')
        logging.info('Found %d rows after search', len(rows))
        for row in rows:
            logging.info('Row content: [%s]', row.text)
            
        time.sleep(1)  # Final wait for any updates


######################################################################
# These functions are for verifying messages and results
######################################################################

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    assert(found)

@then('I should see "{name}" in the results')
def step_impl(context, name):
    # Log what we're looking for
    logging.info('Looking for %s in search results', name)
    
    found = False
    results_text = ""
    
    for i in range(3):  # Try a few times with a small delay
        try:
            # Get the search results element
            element = context.driver.find_element(By.ID, 'search_results')
            results_text = element.text
            logging.info('Current results (attempt %d): [%s]', i+1, results_text)
            
            if name in results_text:
                found = True
                break
                
            # Get table structure info for debugging
            table = context.driver.find_element(By.CLASS_NAME, 'table')
            rows = table.find_elements(By.TAG_NAME, 'tr')
            logging.info('Table has %d rows', len(rows))
            for idx, row in enumerate(rows):
                logging.info('Row %d contents: [%s]', idx, row.text)
            
            # If not found, wait a bit and try again
            import time
            time.sleep(1)
            
        except Exception as e:
            logging.error("Error checking results (attempt %d): %s", i+1, str(e))
            time.sleep(1)
    
    assert found, f"Could not find '{name}' in results after several attempts. Final results text was: [{results_text}]"


@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element(By.ID, 'search_results')
    assert(name not in element.text)