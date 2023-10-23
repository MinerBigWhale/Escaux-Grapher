import os
import csv
import sys
import glob
import json
import time
from colorama import init, Fore
from configparser import ConfigParser
import networkx as nx
import matplotlib.pyplot as plt


from dbmanager import Database
from download import WebView
from invoices import Invoices



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
    
    
    
    web = WebView(config, db)
    print("Webview Ready")
    web.get_phones()
    web.get_phones_status(1)
    web.get_phones_status(2)
    web.get_extensions()
    web.get_ddi()
    web.get_queues()
    
    
    inv = Invoices(config, db)
    print("Invoices Ready")
    inv.get_invoices()
    
    db.clean()
    print("Database cleaned")
    
    #outputgraph()
    
    
if __name__ == "__main__":
    main()
    
