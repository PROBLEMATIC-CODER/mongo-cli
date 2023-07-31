import re
from pymongo import MongoClient
from datetime import datetime
client = MongoClient("mongodb://localhost:27017")
admin_db = client.admin


RESET = "\033[0m"
RED = "\033[31m"


def format_datetime(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f+05:30")
    date = dt.strftime("%Y-%m-%d")
    time = dt.strftime("%H:%M:%S")

    return date, time


def get_recent_errors(log_length):
    result = admin_db.command('getLog', 'global')

    if 'log' in result:
        error_log = result['log']
        counter = 0
        print(
            RED + f'\nLast {log_length} mongodb logs are given below :\n'+RESET)
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
                print(log_entry)
                print()

                counter += 1
                if counter == log_length:
                    break

            except AttributeError:
                print("Error parsing log entry.")

        print(RED + f'\nLast {log_length} mongodb log ends here\n'+RESET)

    else:
        print("No recent errors found.")
