import yaml
import socket
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, 'port_handler'))
from create_config import create_config_yaml
def check_mongo_running(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(('localhost', port))
        return True
    except ConnectionRefusedError:
        return False
    except socket.timeout:
        return False


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

    except Exception as e:
        create_config_yaml()
        return True
