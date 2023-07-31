import re


def process_value(value):
    if value.startswith("[") and value.endswith("]"):
        # Value is a list
        value = value.strip("[]")
        items = value.split(",")
        processed_items = []
        for item in items:
            processed_items.append(process_value(item))
        return processed_items
    elif value.startswith("{") and value.endswith("}"):
        # Value is an object
        value = value.strip("{}")
        pairs = re.findall(r"(\w+):(\[.*?\]|'.*?'|\{.*?\}|\w+)", value)
        obj = {}
        for key, val in pairs:
            obj[key] = process_value(val)
        return obj
    elif value.startswith("'") and value.endswith("'"):
        # Value is a string
        return value.strip("'")
    elif value.isdigit():
        # Value is an integer
        return int(value)
    else:
        # Value is another type
        return value


def process_insertion_data(command, text_to_replace):
    command = command = command.strip()
    command = command.replace(text_to_replace, "")

    pairs = re.findall(r"(\w+):(\[.*?\]|'.*?'|\{.*?\}|\w+)", command)
    data = {}

    for key, value in pairs:
        data[key] = process_value(value)

    print(data)
    return data


command = "insert one name:Shashank,code:['shashank',2,3],data:{class:10th,more:[1,2,3],moredata:{class:8th},nested:{a:[1,2,3],b:{c:[4,5,6]}}}"

process_insertion_data(command)
