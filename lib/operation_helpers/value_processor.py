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

def split_command_fields(command):
    fields = []
    field = ""
    within_list = False

    for char in command:
        if char == "," and not within_list:
            fields.append(field.strip())
            field = ""
        else:
            if char == "[":
                within_list = True
            elif char == "]":
                within_list = False
            field += char

    fields.append(field.strip())

    return fields

def extract_value_from_filter(command) -> str:
    operators = ['eq','ne','gt','lt','gte','lte','in','nin','regex','or','contains','task']

    operator_pattern = '|'.join(re.escape(op) for op in operators)

    pattern = r'eq\s+(.*?)\s+(?={})'.format(operator_pattern)
    

    match = re.search(pattern, command)
    if match:
        extracted_part = match.group(1)
        return extracted_part.strip()
    else:
        return command

def split_string_by_operator(command):
    result = []
    current_part = ""
    operators = ['eq','ne','gt','lt','gte','lte','in','nin','regex','or','contains','task']
    i = 0
    if len(command) > 1:
        while i < len(command):
            match_found = False
            for operator in operators:
                if command[i:i+len(operator)].lower() == operator:
                    print('this is running')
                    if current_part:
                        result.append(current_part.strip())
                    result.append(operator)
                    current_part = ""
                    i += len(operator)
                    match_found = True
                    break
            
            if not match_found:
                current_part += command[i]
                i += 1
        
        if current_part:
            result.append(current_part.strip())
    else:
        result.append(command)
    
    return result