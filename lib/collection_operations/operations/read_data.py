import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))

from utils.text_colors import GREEN,PURPLE,RESET,YELLOW,RED


def get_collection_data(collection,db,current_collection,format_document): 
    try:
        if(collection != None and db != None):
            documents = db[current_collection].find()
            data = []
            document_count = collection.count_documents({})
            if(document_count > 0):
                print(
                    GREEN+f"\nDocuments of collection {current_collection} is given below - \n" + RESET)
                for document in documents:
                    formatted_data = format_document(document)
                    print(PURPLE + f'\n{formatted_data}'+RESET)
                return True
            else:
                print(
                    YELLOW + '\nCollection is empty!, you can use "insert" command for inserting documents' + RESET)

        else:
            print(RED+f"\nERROR: Invalid process of reading documents"+RESET)
            return False
    except:
        print(RED + "\nUnable to read collection documents" + RESET)
        return False