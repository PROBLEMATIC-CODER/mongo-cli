import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


def check_collection_exists(client,db_name, collection_name):
    db = client[db_name]
    available_collections = db.list_collection_names()
    lowercase_collection = [item.strip().lower()
                            for item in available_collections]
    if(collection_name.lower() in lowercase_collection):
        return True
    else:
        return False
