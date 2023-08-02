import re 
import sys,os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from utils.text_colors import RED,RESET
def process_value(value):
    if value is None:
        return None

    if type(value) != int and type(value) != bool:
        if value.startswith("[") and value.endswith("]"):
            value = value.strip("[]")
            items = value.split(",")
            processed_items = []
            for item in items:
                processed_items.append(process_value(item))
            return processed_items
        elif value.startswith("{") and value.endswith("}"):
            value = value.strip("{}")
            pairs = re.findall(r"(\w+):(\[.*?\]|'.*?'|\{.*?\}|[\w\s]+)", value)
            obj = {}
            for key, val in pairs:
                obj[key] = process_value(val)
            return obj
        elif value.startswith("'") and value.endswith("'"):
            return value.strip("'")

        elif value.isdigit():
            return int(value)
        elif value.lower() == 'true' or value.lower() == 'false':
            return bool(value)
        elif(value == 'null'):
            return None
        return value
    else:
        return value


def process_insertion_data(command):
    command = command.strip()
    command = command.replace("insert", "")
    if(len(command) > 0):
        pairs = re.findall(
            r"(\w+)\seq\s(\[.*?\]|'.*?'|\{.*?\}|[\w\s]+)", command)
        data = {}

        for key, value in pairs:
            data[key] = process_value(value)

        return data
    else:
        print(RED+'\nERROR: Please give data to insert in the document'+RESET)
        return False


def process_direct_insertion_data(data):
    if(len(data) > 0):
        pairs = re.findall(r"(\w+):(\[.*?\]|'.*?'|\{.*?\}|[\w\s]+)", data)
        storage = {}

        for key, value in pairs:
            key, value = key.strip(), value.strip()
            storage[key] = process_value(value)

        return storage
    else:
        print(RED+'\nERROR: Please give data to insert in the document'+RESET)
        return False


def process_insertion_many_data(data):
    processed_data = {}
    pairs = data.split(',')
    pairs = [pair.strip() for pair in pairs]
    for pair in pairs:
        pair_parts = pair.split(' eq ')
        key, value = pair_parts[0], pair_parts[1]
        value = process_value(value)
        processed_data[key] = value
    return processed_data

