import yaml
import socket


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

    except:
        return False
