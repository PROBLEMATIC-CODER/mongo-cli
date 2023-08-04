def is_list(value):
    if value.startswith("[") and value.endswith("]"):
        return True
    else:
        return False


def check_type_array(document, key_to_check: str) -> bool:
    try:
        if isinstance(document[key_to_check], list):
            return True
        else:
            return False
    except:
        return False


def is_dict(value):
    return value.startswith('{') and value.endsWith('}')


