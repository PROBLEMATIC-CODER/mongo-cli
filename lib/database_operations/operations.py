import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))
from utils.text_colors import GREEN,GRAY,BOLD,YELLOW,RESET,RED
from check_exists import *

def showDB(client):
    databases = client.list_database_names()
    if len(databases) > 0:
        print(GREEN + '\nAvailable Databases :\n')
        for i, database in enumerate(databases, start=1):
            print(GRAY + BOLD + f' {i}. ' + YELLOW + database + RESET)
        return True
    else:
        print(YELLOW + "\nNo Database available, use 'create database' command to create one"+RESET)
        return True
    

def create_database(client,database_name: str) -> bool:
    try:
        do_db_exists = check_db_exists(client,database_name.strip())
        if(not do_db_exists['exists']):
            new_database = client[f'{database_name.strip()}']
            if new_database is not None:
                initial_collection = new_database['data']
                initial_collection.insert_one(
                    {'from': 'MongoDB Controller CLI', 'description': "This document is initially added by the MongoDB Controller CLI. You can delete it."})
                print(
                    GREEN + f"\nSuccessfully created {database_name}, you can access it using 'run {database_name}'"+RESET)
                return True
            else:
                print(RED + "\nUnable to create database"+RESET)
                return False
        else:
            print(
                YELLOW + f"\nDatabase with name {database_name} already exists, try again with another name!"+RESET)
            return False
    except Exception as e:
        print(
            RED + f"\nAn error occurred while creating the database: {e}"+RESET)
        return False


def drop_db(client,name):
    check_exists = check_db_exists(client,name.strip())
    if(check_exists['exists'] == True):
        try:
            client.drop_database(name.strip())
            print(GREEN + "\nDatabase dropped successfully"+RESET)
            return True
        except Exception as e:
            print(
                RED + f"\nERROR: An error occurred while deleting the database: {e}" + RESET)
            return False
    else:
        print(
            RED + f"\nERROR : No such database with name {name.strip()}"+RESET)
        return False





