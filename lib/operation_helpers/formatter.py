from bson import ObjectId
from json import JSONEncoder
import json
import datetime
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)


def format_key_value(key, value):
    if key == "_id":
        return f"{key}: {str(value)}"
    elif isinstance(value, str):
        return f"{key}: {value}"
    else:
        return f"{key}: {json.dumps(value, cls=CustomJSONEncoder)}"


def format_document(document):
    formatted_data = "{\n"
    for key, value in document.items():
        formatted_data += f"    {format_key_value(key, value)},\n"
    formatted_data = formatted_data.rstrip(",\n") + "\n"
    formatted_data += "}"

    return formatted_data

