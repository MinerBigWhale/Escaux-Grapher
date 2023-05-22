import os
import csv
import sys
import glob
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
import sqlite3
from sqlite3 import Error
import networkx as nx
import matplotlib.pyplot as plt

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
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                file_name = fname[:-11]
                dl_wait = True
    return file_name
    

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        try:
            self.cur.execute('''CREATE TABLE users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                extension TEXT,
                                description TEXT,
                                department TEXT,
                                site TEXT,
                                phone1 TEXT,
                                phone2 TEXT,
                                assist TEXT,
                                cfu TEXT,
                                sdaction TEXT,
                                team TEXT,
                                alt TEXT,
                                reception TEXT
                            )''')
            self.cur.execute('''CREATE TABLE queues (
                                id TEXT PRIMARY KEY,
                                extension TEXT,
                                description TEXT,
                                department TEXT,
                                site TEXT,
                                oooh TEXT,
                                lunch TEXT,
                                holiday TEXT,
                                sdaction TEXT,
                                nomember TEXT,
                                name TEXT
                            )''')
            self.cur.execute('''CREATE TABLE queuemember (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                aqa TEXT,
                                queue TEXT,
                                phone TEXT
                            )''')
            self.cur.execute('''CREATE TABLE ivrs (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                extension TEXT,
                                description TEXT,
                                department TEXT,
                                site TEXT,
                                oooh TEXT,
                                lunch TEXT,
                                holiday TEXT,
                                noinput TEXT
                            )''')
            self.cur.execute('''CREATE TABLE ivrchoise (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                ivr INTEGER,
                                dtmf INTEGER,
                                choise TEXT
                            )''')
            self.cur.execute('''CREATE TABLE phones (
                                id TEXT PRIMARY KEY,
                                type TEXT,
                                mac TEXT,
                                ip TEXT,
                                isConnected BINARY
                            )''')
            self.cur.execute('''CREATE TABLE extension (
                                id TEXT PRIMARY KEY,
                                type TEXT,
                                description TEXT
                            )''')
            self.cur.execute('''CREATE TABLE redirection (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                origin TEXT,
                                destination TEXT,
                                type TEXT,
                                description TEXT
                            )''')
            self.conn.commit()
        except Exception as e:
            print(f"Failed to create tables: {e}")
            print(f"Ensure you are not connected to the DB")
            
    def insert_user(self, extension, description, department, site, phone1, phone2, assist, cfu, sdaction, team, alt, reception):
        try:
            self.cur.execute('''INSERT INTO users (extension, description, department, site, phone1, phone2, assist, cfu, sdaction, team, alt, reception)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (extension, description, department, site, phone1, phone2, assist, cfu, sdaction, team, alt, reception))
        except:
            print('-')
        
    def insert_queue(self, extension, description, department, site, oooh, lunch, holiday, sdaction, nomember, name):
        try:    
            self.cur.execute('''INSERT INTO queues (extension, description, department, site, oooh, lunch, holiday, sdaction, nomember, name)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (extension, description, department, site, oooh, lunch, holiday, sdaction, nomember, name))
        except:
            print('-')
        
    def insert_queuemember(self, aqa, queue, phone):
        try:
            self.cur.execute('''INSERT INTO queuemember (aqa, queue, phone) 
                                VALUES (?, ?, ?)''', 
                                (aqa, queue, phone))
        except:
            print('-')
        
    def insert_ivr(self, extension, description, department, site, oooh, lunch, holiday, noinput):
        try:
            self.cur.execute('''INSERT INTO ivrs (extension, description, department, site, oooh, lunch, holiday, noinput)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                (extension, description, department, site, oooh, lunch, holiday, noinput))
        except:
            print('-')
        
    def insert_ivr_choice(self, ivr, dtmf, choice):
        try:
            self.cur.execute('''INSERT INTO ivrchoise (ivr, dtmf, choise) 
                                VALUES (?, ?, ?)''', 
                                (ivr, dtmf, choice))
        except:
            print('-')
        
    def insert_redirection(self, origin, destination, type, description):
        try:
            self.cur.execute('''INSERT INTO redirection (origin, destination, type, description) 
                                VALUES (?, ?, ?, ?)''', 
                                (origin, destination, type, description))
        except:
            print('insert_redirection')
        
    def insert_phone(self, id, type, mac, ip, is_connected):
        try:
            self.cur.execute('''INSERT INTO phones (id, type, mac, ip, isConnected) 
                                VALUES (?, ?, ?, ?, ?)''', 
                                (id, type, mac, ip, is_connected))
        except:
            print('-')
        
    def insert_extension(self, id, type, description):
        try:
            self.cur.execute('''INSERT INTO extension (id, type, description) 
                                VALUES (?, ?, ?)''', 
                                (id, type, description))
        except:
            print('-')
        
    def find_redirection_phone(self, queue_name, phone_id, redirection_type, description):
        try:
            self.cur.execute('''INSERT INTO redirection (origin, destination, type, description)
                                SELECT queues.id, users.extension, ?, ?
                                FROM queues, users
                                WHERE queues.name = ? AND (users.phone1 = ? OR users.phone2 = ?)''',
                                (redirection_type, description, queue_name, phone_id, phone_id))
        except:
            print('find_redirection_phone')
    def find_redirection_user(self, queue_name, user_ext, redirection_type, description):
        try:
            self.cur.execute('''INSERT INTO redirection (origin, destination, type, description)
                                SELECT queues.id, ?, ?, ?
                                FROM queues,
                                WHERE queues.name = ?''',
                                (user_ext, redirection_type, description, queue_name))
        except:
            print('find_redirection_user')
                            
    def commit(self):
        self.conn.commit()
        
    def select_users(self):
        self.cur.execute("SELECT * FROM users")
        return self.cur.fetchall()
        
    def select_queues(self):
        self.cur.execute("SELECT * FROM queues")
        return self.cur.fetchall()
        
    def select_queuemember(self):
        self.cur.execute("SELECT * FROM queuemember")
        return self.cur.fetchall()
        
    def select_ivrs(self):
        self.cur.execute("SELECT * FROM ivrs")
        return self.cur.fetchall()
        
    def select_ivrchoise(self):
        self.cur.execute("SELECT * FROM ivrchoise")
        return self.cur.fetchall()
        
    def select_redirection(self):
        self.cur.execute("SELECT * FROM redirection")
        return self.cur.fetchall()
        
    def select_phones(self):
        self.cur.execute("SELECT * FROM phones")
        return self.cur.fetchall()
        
    def select_extension(self):
        self.cur.execute("SELECT * FROM extension")
        return self.cur.fetchall()
    
    def update_user(self, user_id, extension=None, description=None, department=None, site=None, phone1=None, phone2=None, assist=None, cfu=None, sdaction=None, team=None, alt=None, reception=None):
        # Construct the SQL statement dynamically based on which parameters were passed in
        update_query = "UPDATE users SET "
        update_values = []
        if extension is not None:
            update_query += "extension = ?, "
            update_values.append(extension)
        if description is not None:
            update_query += "description = ?, "
            update_values.append(description)
        if department is not None:
            update_query += "department = ?, "
            update_values.append(department)
        if site is not None:
            update_query += "site = ?, "
            update_values.append(site)
        if phone1 is not None:
            update_query += "phone1 = ?, "
            update_values.append(phone1)
        if phone2 is not None:
            update_query += "phone2 = ?, "
            update_values.append(phone2)
        if assist is not None:
            update_query += "assist = ?, "
            update_values.append(assist)
        if cfu is not None:
            update_query += "cfu = ?, "
            update_values.append(cfu)
        if sdaction is not None:
            update_query += "sdaction = ?, "
            update_values.append(sdaction)
        if team is not None:
            update_query += "team = ?, "
            update_values.append(team)
        if alt is not None:
            update_query += "alt = ?, "
            update_values.append(alt)
        if reception is not None:
            update_query += "reception = ?, "
            update_values.append(reception)
        # Remove the trailing comma and space
        update_query = update_query[:-2]
        # Add the WHERE clause to update only the specified user
        update_query += "WHERE id = ?"
        update_values.append(user_id)
        # Execute the SQL statement and commit the transaction
        self.cur.execute(update_query, tuple(update_values))
        self.conn.commit()
    
    def update_queue(self, queue_id, extension=None, description=None, department=None, site=None, oooh=None, lunch=None, holiday=None, sdaction=None, nomember=None):
        # Construct the SQL UPDATE statement dynamically based on the provided arguments
        update_query = 'UPDATE queues SET '
        update_values = []
        if extension is not None:
            update_query += 'extension = ?, '
            update_values.append(extension)
        if description is not None:
            update_query += 'description = ?, '
            update_values.append(description)
        if department is not None:
            update_query += 'department = ?, '
            update_values.append(department)
        if site is not None:
            update_query += 'site = ?, '
            update_values.append(site)
        if oooh is not None:
            update_query += 'oooh = ?, '
            update_values.append(oooh)
        if lunch is not None:
            update_query += 'lunch = ?, '
            update_values.append(lunch)
        if holiday is not None:
            update_query += 'holiday = ?, '
            update_values.append(holiday)
        if sdaction is not None:
            update_query += 'sdaction = ?, '
            update_values.append(sdaction)
        if nomember is not None:
            update_query += 'nomember = ?, '
            update_values.append(nomember)
        
        # Remove the last comma and space from the query string
        update_query = update_query[:-2]
        
        # Add the WHERE clause to specify which row to update
        update_query += ' WHERE id = ?'
        update_values.append(queue_id)
        
        # Execute the SQL statement with the provided values
        self.cur.execute(update_query, update_values)
        self.conn.commit()
    
    def update_phone(self, phone_id, phone_type=None, mac=None, ip=None, is_connected=None):
        # Construct the SQL UPDATE statement dynamically based on the provided arguments
        update_query = 'UPDATE phones SET '
        update_values = []
        if phone_type is not None:
            update_query += 'type = ?, '
            update_values.append(phone_type)
        if mac is not None:
            update_query += 'mac = ?, '
            update_values.append(mac)
        if ip is not None:
            update_query += 'ip = ?, '
            update_values.append(ip)
        if is_connected is not None and is_connected == 1:
            update_query += 'isConnected = ?, '
            update_values.append(is_connected)
        
        # Remove the last comma and space from the query string
        update_query = update_query[:-2]
        
        # Add the WHERE clause to specify which row to update
        update_query += ' WHERE id = ?'
        update_values.append(phone_id)
        
        # Execute the SQL statement with the provided values
        self.cur.execute(update_query, update_values)
        self.conn.commit()
    
    
    def get_extension_nodes(self):
        self.cur.execute('SELECT extension.id, extension.type, extension.description FROM extension inner join redirection on extension.id = redirection.origin or extension.id = redirection.destination')
        rows = self.cur.fetchall()
        nodes = [(row[0], {'type': row[1], 'description': str(row[0]) + row[2]}) for row in rows]
        #print(nodes)
        return nodes
        
    def get_redirection_edges(self):
        self.cur.execute('SELECT origin, destination, type, description FROM redirection')
        rows = self.cur.fetchall()
        edges = [(row[0], row[1], {'type': row[2], 'description': row[3]}) for row in rows]
        #print(edges)
        return edges
        
    def clean(self):
        self.cur.execute("DELETE FROM redirection WHERE origin IS NULL OR destination IS NULL OR origin = '' OR destination = ''")
        self.conn.commit()

def outputgraph():
    global db
    print('display result')
    # Create the graph
    G = nx.DiGraph()

    # Add nodes
    extension_nodes = db.get_extension_nodes()
    G.add_nodes_from(extension_nodes)

    # Add edges
    redirection_edges = db.get_redirection_edges()
    G.add_edges_from(redirection_edges)


    G.remove_nodes_from(list(nx.isolates(G)))

    # Remove nodes without 'type' attribute
    nodes_with_type = [node for node in G.nodes() if 'type' in G.nodes[node]]
    G = G.subgraph(nodes_with_type)

    # Define styles
    node_colors = {'User': 'lightblue', 'Manager': 'blue', 'Queue': 'lightgreen', 'IVR': 'yellow'}
    edge_styles = {'next': 'solid', 'member': 'dashed', 'unvail': 'dotted'}

    node_color_list = [node_colors[G.nodes[node]['type']] for node in G.nodes()]
    edge_style_list = [edge_styles[G.edges[edge]['type']] for edge in G.edges()]


    # Draw the graph
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color=node_color_list, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edge_color='gray', style=edge_style_list, alpha=0.8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(edge[0], edge[1]): G.edges[edge]['description'] for edge in G.edges()})
    nx.draw_networkx_labels(G, pos, labels={node: G.nodes[node]['description'] for node in G.nodes()})

    plt.axis("off")
    plt.show()

        
class WebView:
    def __init__(self):
        global config
        print(f"Connecting to SMP")
        with open("credential.json", "r") as f:
            credentials = json.load(f)
            username = credentials["username"]
            password = credentials["password"]
        CHROME_DRIVER_PATH = config.get("files", "chromedriver")
        DOWNLOAD_PATH = config.get("files", "tempfolder")
        DURATION = config.getint("delay", "cooldown")
        try :
            options = webdriver.ChromeOptions()
            #options.add_argument('--headless')
            prefs = {"download.default_directory" : resource_path(DOWNLOAD_PATH)};
            options.add_experimental_option("prefs", prefs);
            self.driver = webdriver.Chrome(resource_path(CHROME_DRIVER_PATH), options=options)
            URL = config.get("website", "login")
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
        self.driver.close()

        
    def get_phones(self):
        global config, db
        print(f"Getting phone list")
        URL = config.get("website", "phone")
        WAIT = config.getint("delay", "maxwait")
        self.driver.get(URL)
        wait = WebDriverWait(self.driver, WAIT)
        wait.until(EC.presence_of_all_elements_located((By.NAME, "templatedata")))
        templatedata_form_radio = self.driver.find_element(By.CSS_SELECTOR, "input[type=radio][name=templatedata][value=all]")
        templatedata_form_radio.click()
        template_form_submit = self.driver.find_element(By.NAME, "template")
        template_form_submit.click()
        
        DOWNLOAD_PATH = config.get("files", "tempfolder")
        download_wait(DOWNLOAD_PATH)
        phone_file = glob.glob(os.path.join(DOWNLOAD_PATH, "import-phone-*.csv"))
        
        with open(phone_file[0]) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')
            print('.')
            for row in reader:
                if 'SDX6' in row['RESOURCEID']:
                    continue 
                    
                db.insert_phone(row['RESOURCEID'], row['VERSION'], row['MAC'], "unknown", 0)
        db.commit()        
        

    
    def get_phones_status(self,id):
        global config, db
        print(f"Getting phone status")
        URL = config.get("website", "phonesop"+str(id))
        WAIT = config.getint("delay", "maxwait")
        self.driver.get(URL)
        wait = WebDriverWait(self.driver, WAIT)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.pme-row-0")))
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Find all rows with class 'pme-row-0'
        rows = soup.select('tr.pme-row-0')

        # Loop through each row and print the text of its td elements
        
        print('.')
        for row in rows:
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
                db.update_phone(row_data[0], ip=status[status.index('172'):-1], is_connected=1)
        db.commit()        
                
    def get_extensions(self):
        global config, db
        print(f"Getting extension list")
        URL = config.get("website", "directory")
        WAIT = config.getint("delay", "maxwait")
        self.driver.get(URL)
        wait = WebDriverWait(self.driver, WAIT)
        wait.until(EC.presence_of_all_elements_located((By.NAME, "templatedata")))
        templatedata_form_radio = self.driver.find_element(By.CSS_SELECTOR, "input[type=radio][name=templatedata][value=all]")
        templatedata_form_radio.click()
        template_form_submit = self.driver.find_element(By.NAME, "template")
        template_form_submit.click()
        
        DOWNLOAD_PATH = config.get("files", "tempfolder")
        download_wait(DOWNLOAD_PATH)
        directory_file = glob.glob(os.path.join(DOWNLOAD_PATH, "import-directory-*.csv"))

        with open(directory_file[0]) as csv_file:
            print('.')
            reader = csv.DictReader(csv_file, delimiter=';')
            for row in reader:
                if "Template-CallQueuer." in row["PROFILE"]:
                    db.insert_extension(row["EXTENSION"][1:], 'Queue', row["FIRSTNAME"]+" "+row["LASTNAME"])
                    db.insert_queue(row["EXTENSION"][1:], row["FIRSTNAME"]+" "+row["LASTNAME"], row["DEPARTMENT"], row["SITE"], row["VAR11"][1:], row["VAR13"][1:], row["VAR9"][1:], row["VAR15"][1:], row["VAR18"][1:], row["VAR2"][1:])
                    
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR9"][1:],'unvail','holiday')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR11"][1:],'unvail','oooh')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR13"][1:],'unvail','lunch')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR15"][1:],'unvail','sec act')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR18"][1:],'unvail','no member')
                if "Template-IVR." in row["PROFILE"]:
                    db.insert_extension(row["EXTENSION"][1:], 'IVR', row["FIRSTNAME"]+" "+row["LASTNAME"])
                    db.insert_ivr(row["EXTENSION"][1:], row["FIRSTNAME"]+" "+row["LASTNAME"], row["DEPARTMENT"], row["SITE"], row["VAR4"][1:], row["VAR9"][1:], row["VAR2"][1:], row["VAR11"][1:])

                    db.insert_redirection(row["EXTENSION"][1:], row["VAR2"][1:],'unvail','holiday')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR4"][1:],'unvail','oooh')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR9"][1:],'unvail','lunch')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR11"][1:],'member','no imput')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR14"][1:],'next','1')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR16"][1:],'next','2')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR20"][1:],'next','3')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR23"][1:],'next','4')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR26"][1:],'next','5')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR29"][1:],'next','6')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR32"][1:],'next','7')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR35"][1:],'next','8')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR38"][1:],'next','9')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR41"][1:],'next','0')
                if "Template-Manager-" in row["PROFILE"]:
                    db.insert_extension(row["EXTENSION"][1:], 'Manager', row["FIRSTNAME"]+" "+row["LASTNAME"])
                    db.insert_user(row["EXTENSION"][1:], row["FIRSTNAME"]+" "+row["LASTNAME"], row["DEPARTMENT"], row["SITE"], row['PHONE1'], row['PHONE2'], row["VAR20"][1:], row["VAR18"][1:], row["VAR16"][1:], row["VAR31"][1:], row["VAR29"][1:], row["VAR40"][1:])
                    
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR20"][1:],'member','Assist')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR18"][1:],'unvail','CFU')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR16"][1:],'unvail','Busy')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR31"][1:],'unvail','Team')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR29"][1:],'unvail','Alternative')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR40"][1:],'unvail','Reception')
                    
                    db.find_redirection_user(row["VAR21"][1:], row["EXTENSION"][1:],'member','dyn')
                    db.find_redirection_user(row["VAR23"][1:], row["EXTENSION"][1:],'member','dyn')
                    db.find_redirection_user(row["VAR25"][1:], row["EXTENSION"][1:],'member','dyn')
                if "Template-User-" in row["PROFILE"]:
                    db.insert_extension(row["EXTENSION"][1:], 'User', row["FIRSTNAME"]+" "+row["LASTNAME"])
                    db.insert_user(row["EXTENSION"][1:], row["FIRSTNAME"]+" "+row["LASTNAME"], row["DEPARTMENT"], row["SITE"], row['PHONE1'], row['PHONE2'], row["VAR20"][1:], row["VAR18"][1:], row["VAR16"][1:], row["VAR31"][1:], row["VAR29"][1:], row["VAR40"][1:])
                    
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR20"][1:],'member','Assist')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR18"][1:],'unvail','CFU')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR16"][1:],'unvail','Busy')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR31"][1:],'unvail','Team')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR29"][1:],'unvail','Alternative')
                    db.insert_redirection(row["EXTENSION"][1:], row["VAR40"][1:],'unvail','Reception')
                    
                    db.find_redirection_user(row["VAR21"][1:], row["EXTENSION"][1:],'member','dyn')
                    db.find_redirection_user(row["VAR23"][1:], row["EXTENSION"][1:],'member','dyn')
                    db.find_redirection_user(row["VAR25"][1:], row["EXTENSION"][1:],'member','dyn')
        db.commit()        

    def get_queues(self):
        global config, db
        print(f"Getting queue list")
        URL = config.get("website", "queue")
        WAIT = config.getint("delay", "maxwait")
        self.driver.get(URL)
        wait = WebDriverWait(self.driver, WAIT)
        wait.until(EC.presence_of_all_elements_located((By.NAME, "templatedata")))
        templatedata_form_radio = self.driver.find_element(By.CSS_SELECTOR, "input[type=radio][name=templatedata][value=all]")
        templatedata_form_radio.click()
        template_form_submit = self.driver.find_element(By.NAME, "template")
        template_form_submit.click()
        
        DOWNLOAD_PATH = config.get("files", "tempfolder")
        download_wait(DOWNLOAD_PATH)
        queue_file = glob.glob(os.path.join(DOWNLOAD_PATH, "import-queue-*.csv"))

        with open(queue_file[0]) as csv_file:
            print('.')
            reader = csv.DictReader(csv_file, delimiter=';')
            for row in reader:
                for phone in row['VAR11'][1:].split(','): #VAR11 = Members
                    db.insert_queuemember(row["RESOURCEID"][1:], row["VAR1"][1:], phone)
                    db.find_redirection_phone(row["VAR1"][1:], phone,'member','sta')
        db.commit()        
    
def main():
    global config, db, web
    config = ConfigParser()
    config.read("config.ini")
    print("configuration loaded")
    
    TMP_PATH = config.get("files", "tempfolder")
    tmp_forlder = resource_path(TMP_PATH)
    empty_folder(tmp_forlder)
    print("temp folder cleaned")
    
    DB_PATH = config.get("files", "database")
    db_file = resource_path(DB_PATH)
    db = Database(db_file)
    print("Database Ready")
    
    web = WebView()
    web.get_phones()
    web.get_phones_status(1)
    web.get_phones_status(2)
    web.get_extensions()
    web.get_queues()
    
    db.clean()
    print("Database cleaned")
    
    #outputgraph()
    
    
if __name__ == "__main__":
    main()
    
