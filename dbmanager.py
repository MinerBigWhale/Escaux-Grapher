
import sys
import os
import sqlite3
from sqlite3 import Error

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
            sys.stdout.write('iu')
        
    def insert_queue(self, extension, description, department, site, oooh, lunch, holiday, sdaction, nomember, name):
        try:    
            self.cur.execute('''INSERT INTO queues (extension, description, department, site, oooh, lunch, holiday, sdaction, nomember, name)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (extension, description, department, site, oooh, lunch, holiday, sdaction, nomember, name))
        except:
            sys.stdout.write('iq')
        
    def insert_queuemember(self, aqa, queue, phone):
        try:
            self.cur.execute('''INSERT INTO queuemember (aqa, queue, phone) 
                                VALUES (?, ?, ?)''', 
                                (aqa, queue, phone))
        except:
            sys.stdout.write('iqm')
        
    def insert_ivr(self, extension, description, department, site, oooh, lunch, holiday, noinput):
        try:
            self.cur.execute('''INSERT INTO ivrs (extension, description, department, site, oooh, lunch, holiday, noinput)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                (extension, description, department, site, oooh, lunch, holiday, noinput))
        except:
            sys.stdout.write('ii')
        
    def insert_ivr_choice(self, ivr, dtmf, choice):
        try:
            self.cur.execute('''INSERT INTO ivrchoise (ivr, dtmf, choise) 
                                VALUES (?, ?, ?)''', 
                                (ivr, dtmf, choice))
        except:
            sys.stdout.write('iic')
        
    def insert_redirection(self, origin, destination, type, description):
        try:
            self.cur.execute('''INSERT INTO redirection (origin, destination, type, description) 
                                VALUES (?, ?, ?, ?)''', 
                                (origin, destination, type, description))
        except:
            sys.stdout.write('ir')
        
    def insert_phone(self, id, type, mac, ip, is_connected):
        try:
            self.cur.execute('''INSERT INTO phones (id, type, mac, ip, isConnected) 
                                VALUES (?, ?, ?, ?, ?)''', 
                                (id, type, mac, ip, is_connected))
        except:
            sys.stdout.write('ip')
        
    def insert_extension(self, id, type, description):
        try:
            self.cur.execute('''INSERT INTO extension (id, type, description) 
                                VALUES (?, ?, ?)''', 
                                (id, type, description))
        except:
            sys.stdout.write('ie')
        
    def find_redirection_phone(self, queue_name, phone_id, redirection_type, description):
        try:
            self.cur.execute('''INSERT INTO redirection (origin, destination, type, description)
                                SELECT queues.id, users.extension, ?, ?
                                FROM queues, users
                                WHERE queues.name = ? AND (users.phone1 = ? OR users.phone2 = ?)''',
                                (redirection_type, description, queue_name, phone_id, phone_id))
        except:
            sys.stdout.write('frp')
    def find_redirection_user(self, queue_name, user_ext, redirection_type, description):
        try:
            sys.stdout.write('''(?, ?, ?, ?)''',(user_ext, redirection_type, description, queue_name))
            self.cur.execute('''INSERT INTO redirection (origin, destination, type, description)
                                SELECT queues.id, ?, ?, ?
                                FROM queues,
                                WHERE queues.name = ?''',
                                (user_ext, redirection_type, description, queue_name))
        except:
            sys.stdout.write('fru')
                            
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