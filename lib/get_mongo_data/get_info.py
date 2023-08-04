import re
from pymongo import MongoClient
from datetime import datetime
import sys
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'port_handler'))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))

from port_handler.port_operations import get_recent_port
from utils.text_colors import GREEN,RESET

recent_port = get_recent_port()
if(recent_port is not None):
    client = MongoClient(f"mongodb://localhost:{recent_port}")

def get_info():
    admin = client.admin
    server_info = admin.command('serverStatus')
    storage_engine = server_info['storageEngine']['name']
    network_activity = {
        'bytes_in': server_info['network']['bytesIn'],
        'bytes_out': server_info['network']['bytesOut']
    }

    num_connections = server_info['connections']['current']
    active_connections = server_info['connections']['active']

    memory_usage = {
        'resident_memory': server_info['mem']['resident'],
        'virtual_memory': server_info['mem']['virtual']
    }
    host, version, pid, connections, uptime = server_info['host'], server_info[
        'version'], server_info['pid'], server_info['connections'], server_info['uptime']

    print(GREEN + "\nMongoDB informations -\n" + RESET)

    structure = f"Host: {host}\nVersion: {version}\nProcessID: {pid}\nUptime:{uptime}\nStorage Engine: {storage_engine}\nConnections Counts:{num_connections}\nActive Connections:{active_connections}\nNetwork Activities:{network_activity}\nMemory usage:{memory_usage}\n"

    print(structure)

    return server_info

