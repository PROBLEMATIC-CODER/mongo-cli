import os,sys
import pymongo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))

from utils.text_colors import GREEN,RED,RESET,PURPLE

def sort_documents(db,collection,command,format_document):
    if(db is not None and collection is not None):
        command = command.replace('sort', '').strip()
        sorting_pair = command.split(' ')
        sorting_tasks = command.split(' and ')
        sorting_order_in_command = command.split(' in ')
        sorting_arr = sorting_order_in_command[1].split(' ') if len(sorting_order_in_command) > 1 else None
        order = pymongo.ASCENDING
        if len(sorting_order_in_command) > 1:
            given_sorting_order = sorting_arr[0].strip()
            if(given_sorting_order == 'a' or given_sorting_order == 'd'):
                order = pymongo.ASCENDING if given_sorting_order == 'a' else pymongo.DESCENDING

        to_sort_with = sorting_pair[1]

        sorted_docs = list(collection.find().sort(to_sort_with, order))

        print(
            GREEN + f"\nSorted docs in {'ascending' if order == 1 else 'descending'} using {to_sort_with} field is given below - "+RESET) if len(sorting_tasks) <= 1 else print(GREEN + "\nSorted and saved docs successfully. You can see all documents available in collection using 'read all' command"+RESET)

        if(len(sorting_tasks) <= 1):
            for docs in sorted_docs:
                formatted_doc = format_document(docs)
                print(PURPLE + f'\n{formatted_doc}' + RESET)

        if(len(sorting_tasks) > 1):
            task = sorting_tasks[1]
            if(task.lower() == 'save'):
                collection.delete_many({})
                collection.insert_many(sorted_docs)
        return True
    else:
        print(RED + "\nERROR : Process of sorting a collection is invalid" + RESET)
        return False

