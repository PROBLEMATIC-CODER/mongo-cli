import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(SCRIPT_DIR))

sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'operation_helpers'))

from utils.text_colors import GREEN,RED,YELLOW,RESET
from operation_helpers.type_checker import is_list
from operation_helpers.value_processor import *

def delete_documents(db,collection,current_collection):
    if collection != None and db != None:
        document_count = collection.count_documents({})
        if(document_count > 0):
            deletion = collection.delete_many({})
            print(
                GREEN + f'\nSuccessfully deleted all documents of {current_collection}' + RESET)
            print(GREEN + f'\nDelete Count : {deletion.deleted_count}' + RESET)
        else:
            print(GREEN + "\nCollection is already cleared up" + RESET)

    else:
        print(RED+"\nInvalid process to deleting all document"+RESET)

def conditional_delete(command,collection,db,current_collection):
    command = command.replace('delete with', '').strip()
    command_parts = command.split('eq')
    command_parts = [v.strip() for v in command_parts]
    key, value = command_parts[0], command_parts[1]
    if(collection != None and db != None):
        try:
            value = process_value(value)
            processed_deletion_filter = {key: value}
            deletion = collection.delete_many(processed_deletion_filter)
            if(deletion.deleted_count > 0):
                print(
                    GREEN + f"\nSuccessfully Deleted {deletion.deleted_count} documents" + RESET)
                return True
            else:
                print(
                    YELLOW + f"\nNo such document exists with {command} in {current_collection}" + RESET)

                return False
        except Exception as e:
            print(e)
            print(
                RED + f"\nERROR : Any error accured while deleting the documents, error is - {e}"+RESET)
            return False
    else:
        print(RED + f"\nERROR - Invalid process of document deletion" + RESET)
        return False

def delete_selected(db,collection,selected_docs_id,remove_selection,remove_message='show', type='select'):
    if(db != None and collection != None):
        if(len(selected_docs_id) > 0):
            deletion_count = 0
            try:
                collection.delete_many({'_id': {'$in': selected_docs_id}})
                deletion_count += 1
            except Exception as e:
                print(
                    RED+f"\nERROR: Any error accured while deleting the documents- {e}"+RESET)
                return False
            if(type == 'select'):
                print(
                    GREEN+"\nSuccefully deleted recently selected documents from the collection"+RESET)
            else:
                print(GREEN + "\nSuccessfully deleted the filtered documents"+RESET)

            remove_selection(remove_message)
            print(
                YELLOW + "\nSelection has been removed. You can select new documents again."+RESET) if remove_message == 'show' else None

        else:
            print(YELLOW + "\nNothing to delete from selection stack" + RESET)
            return False



