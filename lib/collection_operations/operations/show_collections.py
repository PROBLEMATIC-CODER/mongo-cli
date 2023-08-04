import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))

from utils.text_colors import GREEN,PURPLE,RESET,YELLOW,RED,GRAY


def show_collections(db,current_database):
    if db != None:
        collections = db.list_collection_names()
        if len(collections) > 0:
            print(GREEN + f'\nAvailable Collections of {db.name}:\n' + RESET)
            for index, collection in enumerate(collections, start=1):
                print(GRAY + f'   {index}.' + RESET +
                      YELLOW + f' {collection}' + RESET)
            return True
        else:
            print(
                RED + f"\nDatabase {current_database} is empty, use 'create collection' command to create a collection"+RESET)
            return True
    else:
        print(RED+f"\nNo Databases are choosen yet, please choose a database to see collections or see directly"+RESET)

