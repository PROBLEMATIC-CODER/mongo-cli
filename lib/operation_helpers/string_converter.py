import ast
def convert_string_to_dict(input_str):
    pairs = input_str.split(',')
    result = {}
    for pair in pairs:
        key = key.strip()
        value = value.strip()
        # Process the value to the appropriate data type
        if value.startswith('[') and value.endswith(']'):
            # Value is a list
            value = value.strip('[]')
            value = [int(num) if num.isdigit()
                     else num for num in value.split(',')]
        elif value.startswith('{') and value.endswith('}'):
            # Value is a dictionary
            value = value.strip('{}')
            # Use eval to evaluate the string as a dictionary
            value = eval(value)
        elif value.startswith("'") and value.endswith("'"):
            # Value is a string
            value = value.strip("'")
        elif value.isdigit():
            # Value is an integer
            value = int(value)

        result[key] = value

    return result


def convert_string_to_array(string):
    try:
        array = ast.literal_eval(string)
        if isinstance(array, list):
            return array
        else:
            raise ValueError("Input is not a valid list.")
    except (SyntaxError, ValueError) as e:
        print("Error:", str(e))
        return None


def convert_string_value(value):
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    elif value.lower() == 'null' or len(value) == 0:
        value = None
    elif value.isdigit():
        value = int(value)
    return value



