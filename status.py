import os
import sys
import json
import time
from bs4 import BeautifulSoup
from colorama import init, Fore
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.dirname(__file__)
    
    return os.path.join(base_path, relative_path)
    
def main():
    init()
    with open("credential.json", "r") as f:
        credentials = json.load(f)
        username = credentials["username"]
        password = credentials["password"]

    global config, driver
    config = ConfigParser()
    config.read("config.ini")
    CHROME_DRIVER_PATH = config.get("chromedriver", "path")
    DURATION = config.getint("delay", "cooldown")
    try :
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(resource_path(CHROME_DRIVER_PATH), options=options)
        URL = config.get("website", "login")
        driver.get(URL)
        driver.find_element(By.ID, 'login').click()
        username_form_input = driver.find_element(By.NAME, "username")
        username_form_input.send_keys(username)
        password_form_input = driver.find_element(By.NAME, "password")
        password_form_input.send_keys(password)
        password_form_input.send_keys(Keys.ENTER)
        
        time.sleep(DURATION)
        
        if "login" in driver.current_url:
            raise ConnectionError("login failed")
            
        print(Fore.CYAN + "SOP 1" + Fore.RESET)
        parse_sop("1")
        print(Fore.CYAN + "SOP 2" + Fore.RESET)
        parse_sop("2")
        
    except ConnectionError as err:
        print(f"Unexpected {err=}, {type(err)=}")
    
    finally:
        driver.close()

def parse_sop(id: str) -> str:
    global config, driver
    URL = config.get("website", "phonesop"+id)
    WAIT = config.getint("delay", "maxwait")
    driver.get(URL)
    wait = WebDriverWait(driver, WAIT)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.pme-row-0")))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find all rows with class 'pme-row-0'
    rows = soup.select('tr.pme-row-0')

    # Print the table header
    print('| {:<9} | {:<13} | {:<70} | {:<40} |'.format('ID', 'Status', 'Name', 'Description'))
    print('| {:<9} | {:<13} | {:<70} | {:<40} |'.format('-'*9, '-'*13, '-'*70, '-'*40))

    # Loop through each row and print the text of its td elements
    for row in rows:
        cols = row.select('td')
        if len(cols) < 2:
            continue
            
        #print(cols)
        row_data = [col.text.strip() for col in cols]

        if 'SDX6' in row_data[0]:
            continue 
            
        # Set status color
        status_col = ''
        status_str = ''
        try:
            status = row_data[3].lower()
            if 'is not registered' in status:
                status_col = Fore.RED 
                status_str = 'Unreachable'
            elif 'is registered' in status:
                status_col = Fore.GREEN
                status_str = 'Registered'
        except:
            status_col = ''
            status_str = 'Unknown'

        # Print row with colors
        print('| {:<9} | {}{:<13}{} | {:<70} | {:<40} |'.format(row_data[0], status_col, status_str, Fore.RESET, row_data[2], row_data[3]))

if __name__ == "__main__":
    main()