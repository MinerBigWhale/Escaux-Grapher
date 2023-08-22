import os
import csv
import sys
import wget
import glob
import json
import time
import zipfile
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore
from configparser import ConfigParser
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
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
    
def empty_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                # If the file is a subfolder, recursively empty it
                empty_folder(file_path)
                os.rmdir(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")
            
def download_wait(path_to_downloads):
    dl_wait = True
    file_name = path_to_downloads
    while dl_wait:
        time.sleep(1)
        sys.stdout.write('|')
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                file_name = fname[:-11]
                dl_wait = True
    print("|")
    return file_name
    
def findversion(array, version):
    for item in array:
        if item.get('version') == version:
            return item
    return None
def findplatform(array, platform):
    for item in array:
        if item.get('platform') == platform:
            return item
    return None

def update(version):     
    
    url = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
    response = requests.get(url)
    json_data = response.json()
    
    version_item = findversion(json_data.get('versions'),version)
    platform_item = findplatform(version_item.get('downloads').get('chromedriver'),"win64")
    
    download_url = platform_item.get('url')
    latest_driver_zip = wget.download(download_url,'chromedriver.zip')

    with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
        zip_ref.extractall() # you can specify the destination folder path here
    os.remove(latest_driver_zip)

          
class WebView:
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        
        print(f"Connecting to SMP")
        with open("credential.json", "r") as f:
            credentials = json.load(f)
            username = credentials["username"]
            password = credentials["password"]
        CHROME_DRIVER_PATH = self.config.get("files", "chromedriver")
        DOWNLOAD_PATH = self.config.get("files", "tempfolder")
        DURATION = self.config.getint("delay", "cooldown")
        try :
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            prefs = {"download.default_directory" : resource_path(DOWNLOAD_PATH)};
            options.add_experimental_option("prefs", prefs);
            try :
                self.driver = webdriver.Chrome(resource_path(CHROME_DRIVER_PATH), options=options)
            except SessionNotCreatedException as err:
                print(f"Unexpected {err=}: {err.msg=}")
                if "Current browser version is " in err.msg:
                    indexs = err.msg.find('Current browser version is ')
                    indexe = err.msg.find(' with binary',indexs)
                    version = err.msg[indexs+27:indexe]
                    print(version)
                    update(version)
                    self.driver = webdriver.Chrome(resource_path(CHROME_DRIVER_PATH), options=options)
            URL = self.config.get("website", "login")
            self.driver.get(URL)
            self.driver.find_element(By.ID, 'login').click()
            username_form_input = self.driver.find_element(By.NAME, "username")
            username_form_input.send_keys(username)
            password_form_input = self.driver.find_element(By.NAME, "password")
            password_form_input.send_keys(password)
            password_form_input.send_keys(Keys.ENTER)
            
            time.sleep(DURATION)
            
            if "login" in self.driver.current_url:
                raise ConnectionError("login failed")
                
            print("login success")
            
        except ConnectionError as err:
            print(f"Unexpected {err=}, {type(err)=}")
        
    def __del__(self):
        try:
            self.driver.close()
        except:
            print('Driver is closed')

        
    def get_phones(self):
        print(f"Getting phone list")
        URL = self.config.get("website", "phone")
        WAIT = self.config.getint("delay", "maxwait")
        self.driver.get(URL)
        wait = WebDriverWait(self.driver, WAIT)
        wait.until(EC.presence_of_all_elements_located((By.NAME, "templatedata")))
        templatedata_form_radio = self.driver.find_element(By.CSS_SELECTOR, "input[type=radio][name=templatedata][value=all]")
        templatedata_form_radio.click()
        template_form_submit = self.driver.find_element(By.NAME, "template")
        template_form_submit.click()
        
        DOWNLOAD_PATH = self.config.get("files", "tempfolder")
        download_wait(DOWNLOAD_PATH)
        phone_file = glob.glob(os.path.join(DOWNLOAD_PATH, "import-phone-*.csv"))
        
        with open(phone_file[0]) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')
            for row in reader:
                sys.stdout.write('.')
                if 'SDX6' in row['RESOURCEID']:
                    continue 
                    
                self.db.insert_phone(row['RESOURCEID'], row['VERSION'], row['MAC'], "unknown", 0)
        print('.')
        self.db.commit()        
        

    
    def get_phones_status(self,id):
        print(f"Getting phone status")
        URL = self.config.get("website", "phonesop"+str(id))
        WAIT = self.config.getint("delay", "maxwait")
        self.driver.get(URL)
        wait = WebDriverWait(self.driver, WAIT)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.pme-row-0")))
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Find all rows with class 'pme-row-0'
        rows = soup.select('tr.pme-row-0')

        # Loop through each row and print the text of its td elements
        
        for row in rows:
            sys.stdout.write('.')
            cols = row.select('td')
            if len(cols) < 2:
                continue
                
            #print(cols)
            row_data = [col.text.strip() for col in cols]

            if 'SDX6' in row_data[0]:
                continue 
                
            # Set status color
            status = row_data[3].lower()
            if 'is registered' in status:
                try: 
                    self.db.update_phone(row_data[0], ip=status[status.index('172'):-1], is_connected=1)
                except Exception as e:
                    print(f"E: {e} -> {status}")
        print('.')
        self.db.commit()        
                
    def get_extensions(self):
        print(f"Getting extension list")
        URL = self.config.get("website", "directory")
        WAIT = self.config.getint("delay", "maxwait")
        self.driver.get(URL)
        wait = WebDriverWait(self.driver, WAIT)
        wait.until(EC.presence_of_all_elements_located((By.NAME, "templatedata")))
        templatedata_form_radio = self.driver.find_element(By.CSS_SELECTOR, "input[type=radio][name=templatedata][value=all]")
        templatedata_form_radio.click()
        template_form_submit = self.driver.find_element(By.NAME, "template")
        template_form_submit.click()
        
        DOWNLOAD_PATH = self.config.get("files", "tempfolder")
        download_wait(DOWNLOAD_PATH)
        directory_file = glob.glob(os.path.join(DOWNLOAD_PATH, "import-directory-*.csv"))

        with open(directory_file[0]) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')
            for row in reader:
                sys.stdout.write('.')
                if "Template-CallQueuer." in row["PROFILE"]:
                    self.db.insert_extension(row["EXTENSION"][1:], 'Queue', row["FIRSTNAME"]+" "+row["LASTNAME"])
                    self.db.insert_queue(row["EXTENSION"][1:], row["FIRSTNAME"]+" "+row["LASTNAME"], row["DEPARTMENT"], row["SITE"], row["VAR11"][1:], row["VAR13"][1:], row["VAR9"][1:], row["VAR15"][1:], row["VAR18"][1:], row["VAR2"][1:])
                    
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR9"][1:],'unvail','holiday')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR11"][1:],'unvail','oooh')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR13"][1:],'unvail','lunch')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR15"][1:],'unvail','sec act')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR18"][1:],'unvail','no member')
                if "Template-IVR." in row["PROFILE"]:
                    self.db.insert_extension(row["EXTENSION"][1:], 'IVR', row["FIRSTNAME"]+" "+row["LASTNAME"])
                    self.db.insert_ivr(row["EXTENSION"][1:], row["FIRSTNAME"]+" "+row["LASTNAME"], row["DEPARTMENT"], row["SITE"], row["VAR4"][1:], row["VAR9"][1:], row["VAR2"][1:], row["VAR11"][1:])

                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR2"][1:],'unvail','holiday')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR4"][1:],'unvail','oooh')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR9"][1:],'unvail','lunch')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR11"][1:],'member','no imput')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR14"][1:],'next','1')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR16"][1:],'next','2')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR20"][1:],'next','3')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR23"][1:],'next','4')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR26"][1:],'next','5')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR29"][1:],'next','6')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR32"][1:],'next','7')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR35"][1:],'next','8')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR38"][1:],'next','9')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR41"][1:],'next','0')
                if "Template-Manager-" in row["PROFILE"]:
                    self.db.insert_extension(row["EXTENSION"][1:], 'Manager', row["FIRSTNAME"]+" "+row["LASTNAME"])
                    self.db.insert_user(row["EXTENSION"][1:], row["FIRSTNAME"]+" "+row["LASTNAME"], row["DEPARTMENT"], row["SITE"], row['PHONE1'], row['PHONE2'], row["VAR20"][1:], row["VAR18"][1:], row["VAR16"][1:], row["VAR31"][1:], row["VAR29"][1:], row["VAR40"][1:])
                    
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR20"][1:],'member','Assist')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR18"][1:],'unvail','CFU')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR16"][1:],'unvail','Busy')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR31"][1:],'unvail','Team')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR29"][1:],'unvail','Alternative')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR40"][1:],'unvail','Reception')
                    
                    self.db.find_redirection_user(row["VAR21"][1:], row["EXTENSION"][1:],'member','dyn')
                    self.db.find_redirection_user(row["VAR23"][1:], row["EXTENSION"][1:],'member','dyn')
                    self.db.find_redirection_user(row["VAR25"][1:], row["EXTENSION"][1:],'member','dyn')
                if "Template-User-" in row["PROFILE"]:
                    self.db.insert_extension(row["EXTENSION"][1:], 'User', row["FIRSTNAME"]+" "+row["LASTNAME"])
                    self.db.insert_user(row["EXTENSION"][1:], row["FIRSTNAME"]+" "+row["LASTNAME"], row["DEPARTMENT"], row["SITE"], row['PHONE1'], row['PHONE2'], row["VAR20"][1:], row["VAR18"][1:], row["VAR16"][1:], row["VAR31"][1:], row["VAR29"][1:], row["VAR40"][1:])
                    
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR20"][1:],'member','Assist')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR18"][1:],'unvail','CFU')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR16"][1:],'unvail','Busy')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR31"][1:],'unvail','Team')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR29"][1:],'unvail','Alternative')
                    self.db.insert_redirection(row["EXTENSION"][1:], row["VAR40"][1:],'unvail','Reception')
                    
                    self.db.find_redirection_user(row["VAR21"][1:], row["EXTENSION"][1:],'member','dyn')
                    self.db.find_redirection_user(row["VAR23"][1:], row["EXTENSION"][1:],'member','dyn')
                    self.db.find_redirection_user(row["VAR25"][1:], row["EXTENSION"][1:],'member','dyn')
        print('.')
        self.db.commit()        

    def get_queues(self):
        print(f"Getting queue list")
        URL = self.config.get("website", "queue")
        WAIT = self.config.getint("delay", "maxwait")
        self.driver.get(URL)
        wait = WebDriverWait(self.driver, WAIT)
        wait.until(EC.presence_of_all_elements_located((By.NAME, "templatedata")))
        templatedata_form_radio = self.driver.find_element(By.CSS_SELECTOR, "input[type=radio][name=templatedata][value=all]")
        templatedata_form_radio.click()
        template_form_submit = self.driver.find_element(By.NAME, "template")
        template_form_submit.click()
        
        DOWNLOAD_PATH = self.config.get("files", "tempfolder")
        download_wait(DOWNLOAD_PATH)
        queue_file = glob.glob(os.path.join(DOWNLOAD_PATH, "import-queue-*.csv"))

        with open(queue_file[0]) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')
            for row in reader:
                sys.stdout.write('.')
                for phone in row['VAR11'][1:].split(','): #VAR11 = Members
                    self.db.insert_queuemember(row["RESOURCEID"][1:], row["VAR1"][1:], phone)
                    self.db.find_redirection_phone(row["VAR1"][1:], phone,'member','sta')
        print('.')
        self.db.commit()        