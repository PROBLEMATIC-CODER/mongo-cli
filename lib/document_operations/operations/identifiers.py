import os
import sys
import pymongo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(SCRIPT_DIR))

sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))
from utils.text_colors import RED,RESET,GREEN,PURPLE,YELLOW

def set_identifier(db,collection,globally_selected_docs,selected_docs_id):
    if(db is not None and collection is not None):
        if(len(selected_docs_id) == 0 and len(globally_selected_docs) == 0):
            all_documents = list(collection.find())
            if not all_documents:
                print(YELLOW + "\nNo document in collection !" + RESET)
                return False
            identifier_count = 1
            for doc in all_documents:
                if 'identifier' not in doc:
                    doc['identifier'] = identifier_count
                    identifier_count += 1
            collection.bulk_write(
                [pymongo.ReplaceOne({"_id": doc["_id"]}, doc) for doc in all_documents])
            print(GREEN + "\nSuccessfully added identifiers to all documents"+RESET)
            return True
        else:
            identifier_count = 0
            last_identifier_value = None
            available_documents = list(collection.find({}))  
            for index,doc in enumerate(available_documents):
                if 'identifier' in doc:
                    last_identifier_value = doc['identifier'] - 1
                else: 
                    last_identifier_value = index - 1
                
            
            for index, doc in enumerate(globally_selected_docs):
                if 'identifier' not in doc:
                    last_identifier_value = last_identifier_value + 1   if last_identifier_value is not None else 1
                doc['identifier'] = last_identifier_value
            
            collection.bulk_write(
                [pymongo.ReplaceOne({"_id": doc["_id"]}, doc) for doc in globally_selected_docs])
            print(GREEN + "\nSuccessfully added identifiers to all selected documents" + RESET)
            return True
        
    else:
        print(RED + "ERROR : Invalid process of adding identifiers")
        return True
    
def remove_identifier(db,collection,globally_selected_docs,selected_docs_id):
    if(db is not None and collection is not None):
        if(len(selected_docs_id) == 0 and len(globally_selected_docs) == 0):
            all_documents = list(collection.find())

            if not all_documents:
                print(YELLOW + "\nCollection is empty !"+RESET)
                return False

            for doc in all_documents:
                if 'identifier' in doc:
                    doc.pop('identifier', None)

            collection.bulk_write(
                [pymongo.ReplaceOne({"_id": doc["_id"]}, doc) for doc in all_documents])
            print(GREEN + "\nSuccessfully removed identifiers to all documents"+RESET)
            return True
        else:

            for doc in globally_selected_docs:
                if 'identifier' in doc:
                    doc.pop('identifier', None)
            collection.bulk_write(
                [pymongo.ReplaceOne({"_id": doc["_id"]}, doc) for doc in globally_selected_docs])
            print(
                GREEN + "\nSuccessfully removed identifiers to all selected dcouments" + RESET)
            return True
    else:
        print(RED + "\nERROR : Invalid process of adding identifiers")
        return True

            
  

