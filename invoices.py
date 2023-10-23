import os
import sys
import zipfile
import pandas as pd
from colorama import init, Fore
from configparser import ConfigParser

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
          
class Invoices:
    
    def __init__(self, config, db):
        self.config = config
        self.db = db
        
        
    def extract_excel_data(self, zip_file_path):
        extracted_dir = 'extracted'
        os.makedirs(extracted_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_dir)

            excel_file_path = os.path.join(extracted_dir, "CallDetails.xlsx")
            data = pd.read_excel(excel_file_path)
            return data

        finally:
            empty_folder(extracted_dir)
            os.rmdir(extracted_dir)
            
    def get_invoices(self):
        print(f"Parsing Invoices")
        INVOICES_PATH = self.config.get("files", "invoices")
        folder_path = resource_path(INVOICES_PATH)
        files = os.listdir(folder_path)

        for file in files:
            if file.endswith('.zip'):
                zip_file_path = os.path.join(folder_path, file)
                data = self.extract_excel_data(zip_file_path)

                for index, row in data.iterrows():
                    sys.stdout.write('.')
                    self.db.insert_invoice("+" + str(row["Caller Number"]), row["Call Date"], row["Call Time"], "+" + str(row["Called Nr"]), row["Destination"], row["Country Name"], int(row["Duration"]), float(row["Price(€)"]))

            sys.stdout.write('#')
            self.db.commit()   
        print('.')

        