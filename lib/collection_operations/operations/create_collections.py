import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))


from utils.text_colors import GREEN,RESET,YELLOW,RED

def create_collection(client,db,current_database,collection_name,check_collection_exists) -> bool:
    if(db != None):
        do_collection_exists = check_collection_exists(client,current_database,collection_name.strip())
        if(do_collection_exists == False):
            db.create_collection(collection_name)
            print(
                GREEN + f"\nCollection successfully created with name {collection_name}, you can access this using 'use {collection_name.strip()}'" + RESET)
            return True
        else:
            print(
                YELLOW + f"\nCollection with name {collection_name.strip()} already exists!, try again with another collection name"+RESET)
    else:
        print(RED + f'ERROR : Please choose a database first to create a new collection!'+RESET)
        return False

