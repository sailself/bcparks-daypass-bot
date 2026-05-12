#!/usr/bin/python3

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# Removed webdriver_manager as uc handles it
import time
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
conf = config['General']
pass_date = conf['date']
pass_count = conf['count']
first_name = conf['first_name']
last_name = conf['last_name']
email = conf['email']
email = conf['email']



if __name__ == '__main__':
    print("Initializing browser...")
    driver = uc.Chrome(version_main=147)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    
    driver.get("https://reserve.bcparks.ca/dayuse/registration")
    print("Page loaded.")
    
    # Wait for and scroll to the park button
    button_selector = "[aria-label='Book a pass for Joffre Lakes Provincial Park']"
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    time.sleep(1) # Small pause for any overlay to clear
    
    try: 
        button.click()
        print("Park selected.")
    except Exception as e:
        print(f"Standard click failed: {e}. Trying JavaScript click...")
        driver.execute_script("arguments[0].click();", button)
        print("Park selected (JS).")
    time.sleep(2)
    date_input = wait.until(EC.presence_of_element_located((By.NAME, 'ngbDatepicker'))) # Wait for form
    date_input = driver.find_element(By.NAME, 'ngbDatepicker')
    date_input.clear()
    date_input.send_keys(pass_date)
    
    type_dropdown_elem = wait.until(EC.presence_of_element_located((By.ID, 'passType')))
    type_dropdown = Select(type_dropdown_elem)
    type_dropdown.select_by_value('1: Object')
    
    time_input = wait.until(EC.element_to_be_clickable((By.ID, 'visitTimeDAY')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", time_input)
    time_input.click()
    
    passcount_dropdown_elem = wait.until(EC.presence_of_element_located((By.ID, 'passCount')))
    passcount_dropdown = Select(passcount_dropdown_elem)
    passcount_dropdown.select_by_value(pass_count)
    
    next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class='btn btn-primary']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
    next_button.click()
    print("Selection page submitted.")
    time.sleep(1)
    fname_input = wait.until(EC.presence_of_element_located((By.ID, 'firstName')))
    fname_input.send_keys(first_name)
    lname_input = driver.find_element(By.ID, 'lastName')
    lname_input.send_keys(last_name)
    email_input = driver.find_element(By.ID, 'email')
    email_input.clear()
    email_input.send_keys(email)
    
    # Missing email confirmation field
    try:
        # Try to find the second email field specifically
        email_fields = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='name@example.com']")
        if len(email_fields) > 1:
            email_confirm = email_fields[1]
        else:
            email_confirm = driver.find_element(By.ID, 'emailConfirm')
        
        email_confirm.clear()
        email_confirm.send_keys(email)
    except Exception as e:
        print(f"Could not find or fill confirmation email: {e}")
    # More robust checkbox selection for the MANDATORY agreement
    try:
        agreement_checkbox = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(.,'agree to the above notice')]/../descendant::input[@type='checkbox']")))
    except:
        # Fallback to a broader but still text-linked search
        agreement_checkbox = driver.find_element(By.XPATH, "//label[contains(.,'agree') and contains(.,'notice')]/..//input")
    
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", agreement_checkbox)
    driver.execute_script("arguments[0].click();", agreement_checkbox)
    print("Personal info page filled.")

    # Captcha handling removed as site uses Cloudflare now


    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Submit']/..")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
    try:
        submit_button.click()
    except:
        driver.execute_script("arguments[0].click();", submit_button)

    time.sleep(10)
