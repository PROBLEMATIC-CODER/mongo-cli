from pymongo import MongoClient
import socket
import yaml


def check_mongo_status():
    host = "localhost"
    port = None

    with open('config.yaml', 'r') as f:
        data = yaml.safe_load(f)
    if(data is not None):
        port = data['recent_port']

    try:
        if(port is not None):
            with socket.create_connection((host, port), timeout=5):
                return True
        else:
            return False

    except:
        return False
