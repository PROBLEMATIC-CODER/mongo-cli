import os

import sys
from pymongo import InsertOne
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(SCRIPT_DIR))

sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'operation_helpers'))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', ''))
from utils.text_colors import RED,RESET,GREEN,PURPLE
from operation_helpers.formatter import format_document
from operation_helpers.value_processor import process_insertion_many_data,process_direct_insertion_data

def insert_one(db,collection,data):
    if(collection != None and db != None):
        try:
            insert = collection.insert_one(data)
            document = collection.find_one({'_id': insert.inserted_id})
            formatted_doc = format_document(document)
            print(
                GREEN+f"\nDocument inserted successfully and given below - "+RESET)
            print(PURPLE + f'\n{formatted_doc}'+RESET)
        except Exception as e:
            print(
                RED+f"Error: Insertion couldn't be done because of error : {e}"+RESET)
            return False
    else:
        print(RED+"ERROR: Process of insertion is invalid")

def insert_many(command,db,collection):
    command = command.replace('insert', '').strip()
    if(collection is not None and db is not None):
        documents_to_insert = command.split(' and ')
        bulk_write_operation = []
        try:
            for doc in documents_to_insert:
                processed_document = process_insertion_many_data(doc)
                insertion_query = InsertOne(processed_document)
                bulk_write_operation.append(insertion_query)
            collection.bulk_write(bulk_write_operation)
            print(
                GREEN + "\nSuccessfully inserted documents. You can see them using command 'read all'"+RESET)
            return True

        except Exception as e:
            print(e)
            print(RED + "\nUnable to insert many documents due to some error"+RESET)
            return False

    else:
        print(RED + "\nERROR : Invalid process of inserting documents"+RESET)
        return False

