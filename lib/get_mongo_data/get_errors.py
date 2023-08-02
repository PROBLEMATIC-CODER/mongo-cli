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
from utils.text_colors import GREEN,RESET,RED,PURPLE

recent_port = get_recent_port()

client = MongoClient(f"mongodb://localhost:{recent_port}")
admin_db = client.admin



def format_datetime(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f+05:30")
    date = dt.strftime("%Y-%m-%d")
    time = dt.strftime("%H:%M:%S")

    return date, time


def get_recent_logs(log_length):
    result = admin_db.command('getLog', 'global')

    if 'log' in result:
        error_log = result['log']
        counter = 0
        print(
            GREEN + f'\nLast {log_length} mongodb logs are given below :\n'+RESET)
        for entry in reversed(error_log):
            try:
                datetime_str = re.search(
                    r'"t":{"\$date":"([^"]+)"}', entry).group(1)
                message = re.search(r'"msg":"([^"]+)"', entry).group(1)
                date, time = format_datetime(datetime_str)
                log_entry = {
                    'date': date,
                    'time': time,
                    'message': message
                }
                print(PURPLE + f'\n{log_entry}'+ RESET)

                counter += 1
                if counter == log_length:
                    break

            except AttributeError:
                print(RED + "\nUnable to parse the MongoDB error"+RESET)
                return False

    else:
        print("No recent Logs found.")
