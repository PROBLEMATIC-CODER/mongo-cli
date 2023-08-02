from pymongo import MongoClient
import socket
import yaml
import os,sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(SCRIPT_DIR))

sys.path.append(os.path.join(SCRIPT_DIR, 'port_handler'))
from port_handler.create_config import *


def check_mongo_status():
    host = "localhost"
    port = None

    

    try:
        with open('config.yaml', 'r') as f:
            data = yaml.safe_load(f)
        if(data is not None):
            port = data['recent_port']
        if(port is not None):
            with socket.create_connection((host, port), timeout=5):
                return True
        else:
            return False

    except (FileNotFoundError,Exception) as e:
        create_config_yaml()
        return False

check_mongo_status()