import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))

from utils.text_colors import GREEN,RESET,YELLOW,RED,GREEN

def count(command,client,selected_docs_id,selected_documents_filter,db,collection,current_collection,current_database,command_not_found):
    try:
        command = command.replace('count', '').strip()
        if(command == 'selected'):
            if(selected_docs_id != None):
                count = len(selected_docs_id)
                print(
                    GREEN + f"\nCurrent Filter : {selected_documents_filter}"+RESET)
                print(
                    GREEN + f"\nCount of currently selected {'document is' if count == 1 else 'documents are' }  {count} " + RESET)
                return True
            else:
                print(YELLOW + "\nNothing has been selected yet" + RESET)
                return False
        elif(command == 'documents' or command == 'docs'):
            if(db != None and collection != None):
                documents_count = collection.count_documents({})
                if(documents_count == 0):
                    print(
                        GREEN + f'\nCollection is currently empty user "insert one" command to insert a new document'+RESET)
                    return True
                else:
                    print(
                        GREEN + f"\n{current_collection} collection contains {documents_count} documents init."+RESET)
        elif(command == 'collections' or command == 'collection'):
            if(db != None and client != None):
                collection_count = db.list_collection_names()
                if(len(collection_count) > 0):
                    print(
                        GREEN + f'\n{len(collection_count)} collections {"are" if len(collection_count) > 1 else "is"} currently available in {current_database}' + RESET)
                else:
                    print(
                        YELLOW + f"\nNo collections are currently available in {current_database}, to create use command 'create collection'")
            else:
                print(RED + "\nSelect a database to perform count operation on collections"+RESET)
                return False
        elif(command == 'databases' or command == 'db'):
            if(client != None):
                database_arr = client.list_database_names()
                db_count = len(database_arr)

                if(db_count> 0):
                    print(
                        GREEN + f'\n{db_count} {"databases are" if db_count > 1 else "database is "} currently available in MongoDB')
                else:
                    print(
                        YELLOW + f"\nNo databases are currently available in MongoDB, to create use command 'create db'")
            else:
                print(RED + "\nERROR : Process of getting collection count is invalid")
                return False
        else:
            command_not_found(f'count {command}')
            return False
    except Exception as e:
        print(e)
        print(RED + f"\nERROR : Unable to count {command}")
        return False

