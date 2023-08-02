from json import JSONEncoder
import re
from pymongo import MongoClient
import pymongo
from lib.utils import status
import sys
import os
import keyboard
from lib.utils.controller import restart_controller_child
import json
import socket
from lib.utils.text_colors import RESET, RED, BLUE, GREEN, GRAY, YELLOW, BOLD, PURPLE
import inquirer
from watchdog.events import FileSystemEventHandler
from lib.utils.get_errors import get_recent_errors
from colorama import Fore, Style
from bson import ObjectId
import datetime
from pymongo.operations import UpdateOne, InsertOne
import ast
import yaml
from mongodb_service_handler import start_mongodb_service

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(SCRIPT_DIR))

sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'stages'))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'operation_helpers'))

from lib.stages.linked_stages import LinkedStages
from lib.operation_helpers.formatter import *
from lib.operation_helpers.string_converter import *
from lib.operation_helpers.value_processor import *

print(BLUE+'\n\n----------------------------------------------- Welcome To MongoDB Command Line Control System -----------------------------------------'+RESET + '\n\n')

current_database = ''
current_collection = ''
selected_docs_id = []
globally_selected_docs = []
collection = None
db = None
currentURI = 'MongoDB Controller>'
current_file_path = os.path.abspath(__file__)
last_modified = os.path.getmtime(current_file_path)
selected_documents_filter = ''
linked_stages = LinkedStages()
not_to_move_back = False
not_to_move_forward = False
stage_moved = False
is_home_stage_created = False


def restart_executer():
    path = os.path.abspath(__file__)
    restart_controller_child(path)


class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super().default(obj)


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory and event.src_path == current_file_path:
            self.callback()


def check_save():
    current_modified = os.path.getmtime(current_file_path)
    if current_modified > last_modified:
        return True
    return False


def showStatus():
    if mongoStatus == 'Running':
        print(GREEN+f'\nCurrent MongoDB Status : {mongoStatus} \n'+RESET)
    else:
        print(RED+f'\nCurrent MongoDB Status : {mongoStatus} \n'+RESET)


def commandNotFound(command):
    print(RED+f'\nERROR:No such command found with name {command}'+RESET)
    return True


def showDB():
    databases = client.list_database_names()
    if len(databases) > 0:
        print(GREEN + '\nAvailable Databases :\n')
        for i, database in enumerate(databases, start=1):
            print(GRAY + BOLD + f' {i}. ' + YELLOW + database + RESET)
        return True
    else:
        print(YELLOW + "\nNo Database available, use 'create database' command to create one"+RESET)
        return True


def handle_keypress(event, data):
    key = event.name
    if key == "enter":
        return True

    return False


def chooseDB():
    global current_database
    databases = client.list_database_names()
    choices = [f"{Fore.YELLOW}{db}{Style.RESET_ALL}" if db ==
               current_database else db for db in databases]
    question = [
        inquirer.List(
            'database',
            message='Choose a database',
            choices=choices,
            ignore=True if keyboard.is_pressed('shift') else False
        )
    ]
    answers = inquirer.prompt(question)
    selected_database = answers['database']
    current_database = selected_database
    updateURI(BLUE + current_database)

    access_db = enterInDatabase(current_database, 'checked')
    if access_db:
        print(
            GREEN + f'Successfully accessed {current_database} database' + RESET)
    else:
        print(RED + f"Unable to choose {current_database} database" + RESET)


def updateURI(update):
    global currentURI
    currentURI = f"MongoDB Contoller/{update}>"


def create_stage(stage_name, stage_type, path=None, stage_filter=None, selection_type=None):
    linked_stages.add_stage(linked_stages,stage_name, stage_type,
                            filter=stage_filter, path=path, selection_type=selection_type)
    return True


def clear_selected():
    global selected_documents_filter
    selected_docs_id.clear()
    globally_selected_docs.clear()
    selected_documents_filter = ''


def enterInDatabase(database, type):
    clear_selected()
    try:
        global db
        global current_database
        if(type != 'checked'):
            db_exists = check_db_exists(database.lower())
            if db_exists['exists']:
                current_database = db_exists['name']
                updateURI(current_database)
                db = client[current_database]
                is_exists = linked_stages.do_stage_exists(current_database,linked_stages)
                if(is_exists == False):
                    create_stage(current_database.strip(), 'database')
                else:
                    linked_stages.move_to_existing_stage(current_database,linked_stages)
                return True
            else:
                return False
        else:
            db = client.get_database(database)
            current_database = db.name
            updateURI(current_database)
            return True

    except Exception as e:
        return False


def show_errors():
    get_recent_errors(15)


def show_collections():
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


def enterInCollection(collection_name, type):
    global collection
    global current_collection
    clear_selected()
    if(type == 'checked'):
        collection = db[collection_name]
        current_collection = collection_name
        create_stage(collection_name.strip(), 'collection',
                     f'{current_database}/{current_collection}')
        updateURI(f'{current_database}/{current_collection}')
        print(
            GREEN + f'\nSuccessfully accessed {current_collection} collection of {current_database} database'+RESET)
        return True
    else:
        if(db != None):
            available_collections = db.list_collection_names()
            if(collection_name in available_collections):
                collection = db[collection_name]
                current_collection = collection_name
                is_already = linked_stages.do_stage_exists(current_collection   ,linked_stages)
                if(is_already == False):
                    create_stage(collection_name.strip(), 'collection',
                                 f'{current_database}/{current_collection}')
                else:
                    linked_stages.move_to_existing_stage(current_collection ,linked_stages)
                updateURI(f'{current_database}/{current_collection}')
                print(
                    GREEN + f'\nSuccessfully accessed {current_collection} collection of {current_database} database'+RESET)
                return True
            else:
                print(
                    RED+f"\n No collection found with name {collection_name}")
                return False


def choose_collection():
    global current_collection
    if(db != None):
        collections = db.list_collection_names()
        question = [
            inquirer.List(
                'collection',
                message="Choose a collection",
                choices=collections,
            )
        ]
        answers = inquirer.prompt(question)
        selected_collection = answers['collection']
        current_collection = selected_collection
        enterInCollection(
            current_collection, 'not checked')
        updateURI(f'{current_database}/{current_collection}')
        return True
    else:
        print(RED+f"\nNo Databases are choosen has choosen yet, choose a database to see collections or see directly"+RESET)
        return False


def get_info():
    admin = client.admin
    server_info = admin.command('serverStatus')
    storage_engine = server_info['storageEngine']['name']
    network_activity = {
        'bytes_in': server_info['network']['bytesIn'],
        'bytes_out': server_info['network']['bytesOut']
    }

    num_connections = server_info['connections']['current']
    active_connections = server_info['connections']['active']

    memory_usage = {
        'resident_memory': server_info['mem']['resident'],
        'virtual_memory': server_info['mem']['virtual']
    }
    host, version, pid, connections, uptime = server_info['host'], server_info[
        'version'], server_info['pid'], server_info['connections'], server_info['uptime']

    print(GREEN + "\nMongoDB informations -\n" + RESET)

    structure = f"Host: {host}\nVersion: {version}\nProcessID: {pid}\nUptime:{uptime}\nStorage Engine: {storage_engine}\nConnections Counts:{num_connections}\nActive Connections:{active_connections}\nNetwork Activities:{network_activity}\nMemory usage:{memory_usage}\n"

    print(structure)

    return server_info


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)


def get_collection_data():
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


def delete_documents():
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
        print(RED+"Invalid process to delete document"+RESET)




def conditional_delete(command):
    command = command.replace('delete with', '').strip()
    command_parts = command.split('eq')
    command_parts = [v.strip() for v in command_parts]
    key, value = command_parts[0], command_parts[1]
    if(collection != None and db != None):
        try:
            if(is_list(value) == True):
                value = convert_string_to_array(value)
            value = convert_string_value(value)
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


def drop_database(database_name: str) -> bool:
    check_exists = check_db_exists(database_name)
    if(check_exists['exists'] == True):
        try:
            client.drop_database(database_name)
            print(GREEN + "\nDatabase dropped successfully"+RESET)
            return True
        except Exception as e:
            print(
                RED + f"\nERROR: An error occurred while deleting the database: {e}" + RESET)
            return False
    else:
        print(
            RED + f"\nERROR : No such database with name {database_name}"+RESET)
        return False


def drop_collection(collection_name: str) -> bool:
    if(db != None):
        db.drop_collection(collection_name)
        print(
            GREEN + f"\nCollection with name {collection_name} has been successfully deleted with "+RESET)
        return True
    else:
        print(RED + f'\nERROR : Please choose a database first to drop collection'+RESET)
        return False


def drop(name):
    if(db is None):
        check_exists = check_db_exists(name.strip())
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
    else:
        print(name)
        check_exists = check_collection_exists(current_database, name.strip())
        if(check_exists == True):
            db.drop_collection(name.strip())
            print(
                GREEN + f"\nCollection with name {name.strip()} has been successfully deleted"+RESET)
            return True

        else:
            print(
                YELLOW + f"\nCollection with name {name.strip()} do not exists!, try again with another collection name!"+RESET)
            return False


def create_collection(collection_name: str) -> bool:
    if(db != None):
        do_collection_exists = check_collection_exists(
            current_database, collection_name.strip())
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


def create_database(database_name: str) -> bool:
    try:
        do_db_exists = check_db_exists(database_name.strip())
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


def insert_one(data):
    if(collection != None and db != None):
        try:
            insert = collection.insert_one(data)
            document = collection.find_one({'_id': insert.inserted_id})
            formatted_doc = format_document(document)
            print(
                GREEN+f"\nDocument inserted successfully : {formatted_doc}"+RESET)
        except Exception as e:
            print(
                RED+f"Error: Insertion couldn't be done because of error : {e}"+RESET)
            return False
    else:
        print(RED+"ERROR: Process of insertion is invalid")



def insert_many(command):
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
            print(RED + "\nUnable to insert many documents due to some error"+RESET)
            return False

    else:
        print(RED + "\nERROR : Invalid process of inserting documents"+RESET)
        return False


def insert_one_direct(data, collection_name):
    if(db != None):
        collection_exists = check_collection_exists(
            current_database, collection_name)
        if(collection_exists):
            collection = db[collection_name]
            try:
                insertion = collection.insert_one(data)
                insertion_id = insertion.inserted_id
                doc = collection.find_one({'_id': insertion_id})
                formatted_doc = format_document(doc)
                print(
                    GREEN + f"\nSucccessfully inserted document - \n{formatted_doc}")
                return True
            except Exception as e:
                print(
                    RED + f"\nFailed to insert document because of {e}"+RESET)
                return False
        else:
            print(
                RED+f"\nError: No collection exists with name {collection_name}")
    else:
        print(RED+f"ERROR: Process of insertion invalid"+RESET)


def check_db_exists(name):
    dbs = client.list_database_names()
    lowercase_db = [item.strip().lower() for item in dbs]
    if name.lower() in lowercase_db:
        lower_index = lowercase_db.index(name.lower())
        db_name = dbs[lower_index]
        return {'exists': True, 'name': db_name}
    else:
        return {'exists': False}


def check_collection_exists(db_name, collection_name):
    db = client[db_name]
    available_collections = db.list_collection_names()
    lowercase_collection = [item.strip().lower()
                            for item in available_collections]
    if(collection_name.lower() in lowercase_collection):
        return True
    else:
        return False


def get_direct_access(db_name, collection_name, show_logs=True):
    global db
    global current_database
    global collection
    global current_collection
    clear_selected()
    db_exists = check_db_exists(db_name)
    if db_exists['exists'] == True:
        collection_exists = check_collection_exists(
            db_exists['name'], collection_name)
        if(collection_exists == True):
            db = client[db_exists['name']]
            current_database = db_exists['name']
            collection = db[collection_name]
            current_collection = collection_name
            updateURI(f'{db_exists["name"]}/{collection_name}')
            print(
                GREEN + f' \nSuccefully accessed {collection_name} of {db_name}' + RESET) if show_logs is True else None
            do_stage_exists = linked_stages.do_stage_exists(
                current_collection.strip(),linked_stages)
            if(do_stage_exists == False):
                create_stage(collection_name.strip(), 'collection',
                             f'{current_database}/{current_collection}')
            else:
                linked_stages.move_to_existing_stage(
                    current_collection,linked_stages) if show_logs is True else None
            return True
        else:
            print(
                RED + f"\nERROR: No such collection exists with name {collection_name}" + RESET) if show_logs is True else None
            return False
    else:
        print(
            RED + f"\nERROR: No such database exists with name {db_name}" + RESET) if show_logs is True else None
        return False


def delete_selected(remove_message='show', type='select'):
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
                    GREEN+"\nSuccefully deleted all document from the collection which have been selected recently"+RESET)
            else:
                print(GREEN + "\nSuccessfully deleted the filtered documents"+RESET)

            remove_selection(remove_message)
            print(
                YELLOW + "\nSelection has been removed. You can select new documents again."+RESET) if remove_message == 'show' else None

        else:
            print(YELLOW + "\nNothing to delete from selection stack" + RESET)
            return False


def remove_selection(message='show'):
    global selected_docs_id
    if(db != None and collection != None):
        if(len(selected_docs_id) > 0):
            selected_docs_id = []
            updateURI(f'{current_database}/{current_collection}')
            print(GREEN+"\nSelection has been removed successfully" +
                  RESET) if message == 'show' else None
            return True
        else:
            print(YELLOW+"\nNo documents has been selected yet." +
                  RESET) if message == 'show' else None
            return False
    else:
        print(RED+"\nProcess of removing selection is invalid." +
              RESET) if message == 'show' else None
        return False


def get_selected_value(command):
    command = command.replace('value of', '')
    values_to_get = command.split(',')
    values_to_get = [v.strip() for v in values_to_get]
    print(
        GREEN + f'\nValues of field {",".join(v for v in values_to_get)} is given below - ' + RESET)

    for doc in globally_selected_docs:
        output = []
        for value in values_to_get:
            if value in doc:
                output.append(f'      {value}: {doc[value]}')
            else:
                output.append(f'      {value}: Not Available')

        if(len(values_to_get) == 1):
            formatted_output = "\n{\n" + \
                f"      _id: {doc['_id']},\n" + ',\n'.join(output) + "\n}"
        else:
            formatted_output = "\n{" + \
                f"      \n" + ',\n'.join(output) + "\n}"
        print(PURPLE + formatted_output + RESET)


def select_document(command, show_logs=True, recursive=False):
    global selected_docs_id
    global selected_documents_filter
    global globally_selected_docs
    if(db != None and collection is not None):
        command = command.replace('select', '').strip()
        filter_parts = command.split(' ')
        filtered_docs_id = filter_document(command, 'select')
        if(len(filtered_docs_id) > 0):
            selected_docs = []
            for doc_id in filtered_docs_id:
                doc = collection.find({'_id': doc_id})
                selected_docs.append(doc)
            doc_count = 0
            print(
                GREEN + f"\nSuccefully selected {len(selected_docs)} {'document' if doc_count == 1 else 'documents'}. Selected documents are given below - "+RESET) if show_logs == True else None
            selected_docs_id = []
            globally_selected_docs = []
            for docs in selected_docs:
                for index, doc in enumerate(docs):
                    doc_count += 1
                    globally_selected_docs.append(doc)
                    selected_docs_id.append(doc['_id'])
                    formatted_doc = format_document(doc)
                    print(PURPLE + f"\n{formatted_doc}" +
                          RESET) if show_logs == True else None
            updateURI(
                f'{current_database}/{current_collection}/selected {len(selected_docs_id)} {f"doc" if len(selected_docs_id) ==1 else "docs"} {f"with {command}" if len(filter_parts) <=3 else None}')
            selected_documents_filter = f'{command}'

            filter_to_check = f'selected documents with {command}'
            check_exists = linked_stages.do_stage_exists(filter_to_check,linked_stages)
            if(check_exists == False):
                create_stage(filter_to_check, 'document',
                             f'{current_database}/{current_collection}', command.strip(), 'filtered document')
            else:
                linked_stages.move_to_existing_stage(filter_to_check,linked_stages)
            return True
        else:
            print(
                RED + f"\nNo document found to select with {command} filter" + RESET) if show_logs == True else None
            if(recursive == True):
                remove_selection('do not show')
                print(
                    YELLOW + f'\nSelections has been removed because no document found with filter {selected_documents_filter}, try to select with new filter' + RESET)
            return False
    else:
        print(RED + "\nERROR: Process of selection is invalid" +
              RESET) if show_logs == True else None
        return False


def navigate_home(show='show'):
    global db
    global is_home_stage_created
    global current_database
    global current_collection
    global collection
    db = None
    current_database = None
    current_collection = None
    collection = None
    print(GREEN+'\nWelcome back home !' +
          RESET) if show != 'do not show' else None
    updateURI('')


def show_selected():
    global selected_docs_id
    count = len(selected_docs_id)
    if(count > 0):
        print(
            GREEN + f"\n{count} {'document' if count == 1 else 'documents'} has been selected with given filter, documents are given below - " + RESET)
        for value in globally_selected_docs:
            formatted = format_document(value)
            print("\n"+PURPLE + formatted + RESET)
        return True

    else:
        print(YELLOW + "\nNothing has been selected yet" + RESET)
        return False


def edit_selected_documents(command, reselect=True):
    if collection is not None and db is not None:
        command = command.replace('edit', '')
        parts_to_edit = re.findall(
            r'(\w+\s+eq\s+.*?(?=(?:,\s+\w+\s+eq|\Z)))', command)
        parts_to_edit = [v.strip() for v in parts_to_edit]
        for parts in parts_to_edit:
            part_of_filter = parts.split('eq')
            key, value = part_of_filter[0].strip(), part_of_filter[1].strip()
            value = convert_string_value(value)
            updated_count = 0
            not_updated_count = 0
            not_updated_ids = []
            checked_ids = []
            id_len = len(selected_docs_id)
            for id in selected_docs_id:
                try:
                    filter_criteria = {'_id': id, key: {'$exists': True}}
                    document = collection.find_one(filter_criteria)
                    if document is not None and key in document:
                        value = process_value(value)
                        document[key] = value
                        collection.replace_one(
                            {'_id': document['_id']}, document)

                        if(id not in checked_ids):
                            updated_count += 1
                            checked_ids.append(id)
                    else:
                        if(id not in checked_ids):
                            not_updated_count += 1
                            checked_ids.append(id)
                            not_updated_ids.append(id)
                        continue

                except Exception as e:
                    print(
                        RED + f"ERROR - Any error accured while editing the value error is - {e}" + RESET)
                    if(id not in checked_ids):
                        not_updated_count += 1
                        checked_ids.append(id)
                        not_updated_ids.append(id)
                    continue

            call_to_select_document() if reselect == True else None
            print(
                GREEN + f"\n{updated_count if id_len != updated_count else 'All'} documents have been updated successfully" + RESET) if updated_count > 0 else None
            print(
                YELLOW + f"\nUnable to edit {'document with id' if len(not_updated_ids) == 0 else 'documents with ids - '} {(',').join(str(id) for id in not_updated_ids)}"+RESET) if not_updated_count > 0 else None



def add_fields(command, reselect=True, add_type='select'):
    try:
        if db is not None and collection is not None:
            if len(selected_docs_id) > 0:
                command = command.replace('add', '').strip()
                fields = split_command_fields(command)
                for field in fields:
                    field_separation = field.split('eq', 1)
                    field_separation = [v.strip() for v in field_separation]
                    if len(field_separation) == 2:
                        key = field_separation[0]
                        value = field_separation[1]
                        value = convert_string_value(value)
                        if(value != None):
                            if type(value) == str and value != 'null':
                                if is_list(value):
                                    value = convert_string_to_array(value)
                        update_count = 0
                        ids_not_updated = []
                        not_updated_count = len(ids_not_updated)
                        try:
                            for doc_id in selected_docs_id:
                                update_criteria = {'_id': doc_id}
                                update = {'$set': {key: value}}
                                collection.find_one_and_update(
                                    update_criteria, update)
                                update_count += 1

                        except Exception as e:
                            ids_not_updated.append(doc_id)
                            print(
                                RED + f'\nERROR: Unable to add a new field to the document with id {doc_id} because of an error - {e}')

                call_to_select_document() if reselect == True else None
                print(GREEN + f"\nSuccessfully updated {'all' if len(selected_docs_id) == update_count else update_count} {'filtered' if add_type == 'filter' else 'selected'} documents. You can see the changes by using the command {'show selected' if add_type == 'select' else 'read all'}." + RESET)

                if not_updated_count > 0:
                    print(
                        YELLOW + f"Unable to add the field in {'document with id' if not_updated_count == 1 else 'documents with ids'} {' '.join(ids for ids in ids_not_updated)}." + RESET)

            else:
                print(YELLOW + "\nNothing has been selected yet to add a new field. To add a new field to the whole collection, use the command 'add to all'." + RESET)
                return False
        else:
            print(RED + '\nERROR: The process of adding a new field is invalid.'+RESET)
            return False
    except Exception as e:
        print(
            RED + f'\nERROR: Unable to add field to {"selected documents" if add_type == "select" else "filtered documents"}')

        return False


def split_command_fields(command):
    fields = []
    field = ""
    within_list = False

    for char in command:
        if char == "," and not within_list:
            fields.append(field.strip())
            field = ""
        else:
            if char == "[":
                within_list = True
            elif char == "]":
                within_list = False
            field += char

    fields.append(field.strip())

    return fields


def call_to_select_document():
    if selected_documents_filter == 'select all':
        select_all(False)
    else:
        select_document(f'select {selected_documents_filter}', False, True)
    return True


def remove_field(command, reselect=True):
    try:
        if(collection != None and db != None):
            if(len(selected_docs_id) > 0):
                command = command.replace('remove', '')
                fields_to_remove = command.split(',')
                removed_count = 0
                not_removed_count = 0
                not_removed_id = []
                ids_checked = []
                for field in fields_to_remove:
                    field = field.strip()
                    for ids in selected_docs_id:
                        try:
                            is_exists = collection.find_one(
                                {'_id': ids, field: {'$exists': True}})
                            if(is_exists != None):
                                update_filter = {'_id': ids}
                                update_operation = {'$unset': {field: ''}}
                                collection.update_one(
                                    update_filter, update_operation)
                                if(ids not in ids_checked):
                                    removed_count += 1
                                ids_checked.append(ids)
                            else:
                                print(
                                    YELLOW + f"\nNo such field with name {f'{field}'} found in document with id {ids}"+RESET)
                                not_removed_count += 1
                                not_removed_cred = {'id': ids, 'field': field}
                                not_removed_id.append(not_removed_cred)
                        except Exception as e:
                            not_removed_count += 1
                            not_removed_cred = {'id': ids, 'field': field}
                            not_removed_id.append(not_removed_cred)
                            continue

                call_to_select_document() if reselect == True else None
                print(
                    GREEN + f"\nSuccessfully removed {f','.join(field for field in fields_to_remove)} from {'all' if len(selected_docs_id) == removed_count else f'{removed_count}'} selcted documents"+RESET) if removed_count > 0 else None
                return True
            else:
                print(
                    YELLOW + "\nNo document selected yet to remove the field, select documents to perform this operation"+RESET)
                return False
        else:
            print(RED + "\nERROR : Process of removing field is invalid"+RESET)
            return False
    except Exception as e:
        print(f'A\nny error accured while removing field error is - {e}')


def is_list(value):
    if value.startswith("[") and value.endswith("]"):
        return True
    else:
        return False


def count(command):
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
                        GREEN + f'\nCount of collections available in {current_database} is {len(collection_count)}' + RESET)
                else:
                    print(
                        YELLOW + f"\nNo collections are currently available in {current_database}, to create use command 'create collection'")
            else:
                print(RED + "\nERROR : Process of getting collection count is invalid")
                return False
        else:
            commandNotFound(f'count {command}')
            return False
    except:
        print(RED + f"\nERROR : Unable to count {command}")
        return False


def check_type_array(document, key_to_check: str) -> bool:
    try:
        if isinstance(document[key_to_check], list):
            return True
        else:
            return False
    except:
        return False


def is_dict(value):
    return value.startswith('{') and value.endsWith('}')


def append_in_arr_field(command, type='selection'):
    global selected_documents_filter
    try:
        command = command.replace('append', '')
        append_pairs = command.split(' and ')
        append_pairs = [v.strip() for v in append_pairs]

        if collection is not None and db is not None:
            if len(selected_docs_id) > 0:
                field_not_found = 0
                field_not_found_ids = []
                not_updated_id = []
                not_array_type_count = 0
                updated_count = 0
                checked_id = []
                not_updated_count = 0  # Initialize not_updated_count
                for pairs in append_pairs:
                    value, key = pairs.split('in')
                    value, key = value.strip(), key.strip()
                    values = value.split(',')
                    for val in values:
                        value = process_value(val)
                        for ids in selected_docs_id:
                            check_exists = collection.find_one(
                                {'_id': ids, key: {'$exists': True}})
                            if check_exists is not None:
                                type_arr = check_type_array(check_exists, key)
                                if type_arr:
                                    filter_criteria = {'_id': ids}
                                    update_operation = {'$push': {key: value}}
                                    collection.update_one(
                                        filter_criteria, update_operation)
                                    if ids not in checked_id:
                                        updated_count += 1
                                        checked_id.append(ids)
                                else:
                                    not_array_type_count += 1
                                    if {'field': key, 'id': ids} not in not_updated_id:
                                        not_updated_id.append(
                                            {'field': key, 'id': ids})
                                        not_updated_count += 1
                                        checked_id.append(ids)

                            else:
                                if ids not in field_not_found_ids:
                                    field_not_found += 1
                                    field_not_found_ids.append(ids)

                                continue
                print(
                    GREEN + f'\nSuccessfully appended given values in {"all documents" if updated_count == len(selected_docs_id) else f"{updated_count}"} documents' + RESET) if updated_count > 0 else None

                print(
                    YELLOW + f"\nNo such field found with name '{key}' in {'document with id' if field_not_found == 1 else 'documents with ids'} {','.join(str(id) for id in field_not_found_ids)}" + RESET) if field_not_found > 0 else None

                print(
                    YELLOW + f"\nUnable to update {not_updated_count} documents because the type of '{key}' in documents with ids {','.join(str(v['id']) for v in not_updated_id)} is not an array." + RESET) if not_updated_count > 0 else None

                if(type == 'selection' and updated_count > 0):
                    call_to_select_document()

                return True
            else:
                print(
                    YELLOW + "\nNothing has been selected yet, select a document to perform this operation." + RESET)
        else:
            print(
                RED + "\nInvalid process of appending a value in an array field" + RESET)
            return False

    except Exception as e:
        print(RED + "\nERROR - Any internal error accured or you may have entered invalid command"+RESET)
        return False


def remove_all_elements(lst, element):
    return [x for x in lst if x != element]


def pop_from_arr_field(command, type='selection'):
    command = command.replace('pop', '').strip()
    command_parts = command.split(' ')
    to_delete = command_parts[0]
    delete_all = False
    delete_index = False
    element_len = 0
    if to_delete == 'all':
        command = command.replace('all', '')
        delete_all = True
    elif to_delete == 'index':
        command = command.replace('index', '')
        delete_index = True
    else:
        delete_all = False
    try:
        item, from_field = command.split('from')
        item = process_value(item.strip())
        from_field = from_field.strip()
        if collection is not None and db is not None:
            if len(selected_docs_id) > 0:
                popped_counts = 0
                not_popped_counts = 0
                not_popped_ids = []
                popped_ids = []

                try:
                    for ids in selected_docs_id:
                        filter_to_get_document = {'_id': ids}
                        document = collection.find_one(filter_to_get_document)
                        if document is not None and from_field in document:
                            if isinstance(document[from_field], list):
                                try:
                                    if delete_all:
                                        document[from_field].clear()
                                    elif delete_index:
                                        if(item > len(document[from_field])):
                                            print(
                                                RED + "\nIndex is greater then the length of the array field"+RESET)

                                        document[from_field].pop(item)
                                    else:
                                        elements = item.split(',')
                                        if len(elements) > 1:
                                            element_len = len(elements)
                                            for element in elements:
                                                element = process_value(
                                                    element)
                                                document[from_field].remove(
                                                    element)
                                        else:
                                            document[from_field].remove(item)
                                    filter_criteria = {'_id': ids}
                                    update_operation = {
                                        '$set': {from_field: document[from_field]}}
                                    collection.update_one(
                                        filter_criteria, update_operation)

                                    if(ids not in popped_ids):
                                        popped_counts += 1
                                        popped_ids.append(ids)

                                except ValueError:
                                    if(ids not in not_popped_ids):
                                        not_popped_counts += 1
                                        not_popped_ids.append(ids)
                                    continue
                            else:
                                if(ids not in not_popped_ids):
                                    not_popped_counts += 1
                                    not_popped_ids.append(ids)
                                continue
                        else:
                            if(ids not in not_popped_ids):
                                not_popped_counts += 1
                                not_popped_ids.append(ids)
                            continue
                    not_popped_count = len(selected_docs_id) - popped_counts
                except IndexError as e:
                    pass

            message = GREEN + '\nSuccessfully popped '
            if popped_counts > 0:
                if delete_all:
                    message += 'all elements'
                elif delete_index:
                    message += 'given index'
                else:
                    message += 'given'

                if element_len > 0:
                    message += ' items'
                else:
                    message += ' item'

                message += f' from {from_field}' + RESET

                print(message)

                print(
                    RED + f"\nUnable to pop given items from {f'{not_popped_counts}'} {'documents' if not_popped_counts > 1 else 'document'} with id's - {','.join(str(id) for id in not_popped_ids)} ") if not_popped_count > 0 else None

                call_to_select_document() if type == 'selection' else None
            else:
                print(
                    YELLOW + '\nNothing has been selected yet, select a document to perform this operation.\n' + RESET)
        else:
            print(
                RED + '\nInvalid process of removing item from an array field.\n' + RESET)
            return False
    except ValueError as e:
        print(
            RED + f'\nInvalid format for pop command. Please provide the item and field name to remove from the array. Error: {e}\n' + RESET)
        return False


def search_text(command):
    global selected_documents_filter
    global selected_docs_id
    global globally_selected_docs
    if db is not None and collection is not None:
        command = command.replace('search', '')
        command_pair = command.split('and')
        command_pair = [pair.strip() for pair in command_pair]
        search_pairs = re.split(
            r'(\w+\s+eq\s+.*?(?=(?:,\s+\w+\s+eq|\Z)))', command)
        search_pairs = [pairs.strip() for pairs in search_pairs]
        result = []
        collection.drop_indexes()
        index_name = 'cli_searches'  #
        if index_name not in collection.index_information():
            collection.create_index(
                [('cli_searches', 'text')], name=index_name, default_language='english')
        searched_docs_id = []
        if command_pair[0]:
            pairs = command_pair[0]
            pair = pairs.split('in')
            pair = [p.strip() for p in pair]
            text_to_search, search_in_field = pair[0], pair[1]
            search_query = {}

            search_query[search_in_field] = {
                '$regex': text_to_search, '$options': 'i'}

            searched_docs = collection.find(search_query)

            for docs in searched_docs:
                result.append(docs)
                searched_docs_id.append(docs['_id'])

            if len(result) == 0:
                print(
                    YELLOW + f"\nCan't find any document with '{text_to_search}' text in {search_in_field} field" + RESET)
                return False
            else:
                print(
                    GREEN+f"\nDocuments with {text_to_search} text in {search_in_field} field is given below - "+RESET) if len(command_pair) <= 1 else None
                if len(command_pair) <= 1:
                    for doc in result:
                        doc = format_document(doc)
                        print(PURPLE + f'\n{doc}' + RESET)
                if(len(command_pair) >= 2):
                    if(command_pair[1] == 'select'):
                        selected_docs_id.clear()
                        globally_selected_docs.clear()
                        updateURI(
                            f'{current_database}/{current_collection}/selected {text_to_search} in {search_in_field}')
                        selected_documents_filter = f'{search_in_field} contains {text_to_search}'
                        selected_docs_id.extend(searched_docs_id)
                        globally_selected_docs.extend(result)
                        print(
                            GREEN + f'\nSuccessfully selected documents with {text_to_search} in {search_in_field} field' + RESET)
                    search_selection_filter = f'selected documents with {command}'
                    check_exists = linked_stages.do_stage_exists(
                        search_selection_filter,linked_stages)
                    if(check_exists == False):
                        create_stage(search_selection_filter, 'document',
                                     f'{current_database}/{current_collection}', command, 'searched document')
                    else:
                        linked_stages.move_to_existing_stage(
                            search_selection_filter,linked_stages)
                    return True
                else:
                    return True
    else:
        print(RED + "ERROR: Invalid process of searching text" + RESET)


def sort_collection(command):
    if(db is not None and collection is not None):
        command = command.replace('sort', '').strip()
        sorting_pair = command.split(' ')
        sorting_tasks = command.split(' and ')
        sorting_order_in_command = command.split(' in ')
        order = pymongo.ASCENDING
        if len(sorting_order_in_command) > 1:
            given_sorting_order = sorting_order_in_command[1].strip()
            if(given_sorting_order == 'a' or given_sorting_order == 'd'):
                order = pymongo.ASCENDING if given_sorting_order == 'a' else pymongo.DESCENDING

        to_sort_with = sorting_pair[1]

        sorted_docs = list(collection.find().sort(to_sort_with, order))

        print(
            GREEN + f"\nSorted docs in {'ascending' if order == 1 else 'descending'} using {to_sort_with} field is given below - "+RESET)

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


def create_config_yaml():
    filename = 'config.yaml'
    try:
        # Open the file in 'exclusive creation' mode ('x')
        with open(filename, 'x') as file:
            # Writing to the file (optional)
            file.write("Hello, this is a new file!")
        return True
    except IOError as e:
        return False


def update_port(command):
    try:
        command = command.replace('change port', '').strip()
        key = 'recent_port'
        if command.isdigit():
            running = check_mongo_running(int(command))
            if(running == True):
                try:
                    with open('config.yaml', 'r') as f:
                        data = yaml.safe_load(f)
                        if(data[key] == command):
                            print(GREEN + "\nPort has been updated"+RESET)
                            return True
                    data[key] = command
                    with open('config.yaml', 'w') as f:
                        yaml.dump(data, f)
                    print(
                        GREEN + "\nPort has been updated successfully, restarting the process...."+RESET)
                    main()
                    return True
                except FileNotFoundError:
                    create_config_yaml()
                    update_port(f'change port {command}')
            else:
                print(RED + "\nFailed to connect and update with the given port."+RESET)
                return False

        else:
            print(RED + "\nInvalid port name" + RESET)
        return False
    except Exception as e:
        print(RED + "\nFailed to connect and update with the given port"+RESET)
        return False


def parseCommand(command):
    # try:
    if(len(command) > 0):
        parts = command.lower().strip().split()
        if len(parts) >= 1 and parts[0] == 'run':
            database_name = parts[1]
            if database_name:
                db_access = enterInDatabase(database_name, 'to check')
                if(db_access == True):
                    print(
                        GREEN + f'\nSuccessfully accessed {database_name}' + RESET)
                else:
                    print(
                        RED + f'\nUnable to accessed {database_name} database' + RESET)
        elif command in commands:
            commands[command]()
        elif len(parts) >= 2 and (parts[0] == 'new' or parts[0] == 'create') and parts[1] == 'collection':
            collection_name = parts[2]
            if(collection_name):
                create_collection(collection_name)
        elif (len(parts) >= 2 and (parts[0] == 'new' or parts[0] == 'create') and parts[1] == 'db'):
            database_name = parts[2]
            if(database_name):
                create_database(database_name)
            else:
                commandNotFound(command)
        elif (len(parts) >= 4 and (parts[0] == 'delete' and parts[1] == 'with')):
            conditional_delete(command)
        elif len(parts) == 2 and (parts[0] == 'drop' or parts[0] == 'delete'):
            command_part = command.split(' ')
            name = command_part[1].strip()
            drop(name)
        elif len(parts) >= 3 and (parts[0].lower() == 'use' or parts[0].lower() == 'run') and parts[2] == 'of':
            collection_name = parts[1]
            db_name = parts[3]
            get_direct_access(db_name, collection_name)
        elif db is not None and len(parts) == 2 and parts[0] == 'use':
            parts = command.split(' ')
            collection_name = parts[1].strip()
            enterInCollection(collection_name, 'not checked')

        elif len(parts) >= 3 and parts[0] == 'sort' and parts[1] == 'using':
            sort_collection(command)

        elif (len(parts) >= 3 and parts[0] == 'insert'):
            insertion_type_array = command.split(' and ')
            if len(insertion_type_array) <= 1:
                proccessed_data = process_insertion_data(command)
                if(proccessed_data != False):
                    insert_one(proccessed_data)
                else:
                    print(RED + "\nData processing error"+RESET)
            else:
                insert_many(command)
        elif len(parts) >= 5 and (parts[0] == 'insert' and parts[1] == 'one' and parts[2] == 'in'):
            collection_name = parts[3]
            data = parts[4]
            processed_data = process_direct_insertion_data(data)
            insert_one_direct(processed_data, collection_name)
        elif (len(parts) >= 3 and parts[0] == 'value' and parts[1] == 'of'):
            get_selected_value(command)
        elif (len(parts) >= 2 and parts[0] == 'count'):
            count(command)
        elif(len(parts) >= 4 and parts[0] == 'append'):
            append_in_arr_field(command)
        elif len(parts) >= 4 and parts[0] == 'pop' and parts[2] == 'from':
            pop_from_arr_field(command)
        elif len(parts) >= 5 and parts[0] == 'pop' and parts[1] == 'index' and parts[3] == 'from':
            pop_from_arr_field(command)
        elif len(parts) >= 1 and parts[0] == 'filter':
            filter_document(command, 'filter')
        elif (len(parts) >= 4) and parts[0] == 'search':
            search_text(command)
        elif len(parts) >= 4 and parts[0] == 'add':
            add_fields(command)
        elif(len(parts) >= 2 and parts[0] == 'remove'):
            remove_field(command)
        elif len(parts) >= 4 and parts[0] == 'edit':
            edit_selected_documents(command)
        elif len(parts) >= 4 and parts[0] == 'select':
            select_document(command)
        elif len(parts) >= 4 and parts[0] == 'rename':
            rename_field(command)
        elif len(parts) == 3 and parts[0] == 'change' and parts[1] == 'port':
            update_port(command)
        else:
            print(
                RED+f"\nGiven '{command}' is invalid, please try valid one. To see all commands type commands and press enter"+RESET)
    else:
        print(
            RED + "\nCommand is invalid, please try valid one. To see all commands type commands and press enter.")
        return False
    # except Exception as e:
    #     print(RED + "\nUnable to process command, please try again !"+RESET)
    #     return False


def select_all(show_logs=True):
    global selected_docs_id
    global globally_selected_docs
    global selected_documents_filter
    selected_docs_id.clear()
    globally_selected_docs.clear()
    if(db != None and collection != None):
        try:
            documents = collection.find({})
            for doc in documents:
                selected_docs_id.append(doc['_id'])
                globally_selected_docs.append(doc)
                selected_documents_filter = 'select all'
            updateURI(
                f'{current_database}/{current_collection}/selected all from {current_collection}')
            print(
                GREEN + f"\nSuccessfully selected all documents from {current_collection} collection"+RESET) if show_logs == True else None
            check_exists = linked_stages.do_select_all_exists(
                f"{current_database}/{current_collection}",linked_stages)
            if(check_exists == False):
                create_stage('selected all', 'document',
                             f'{current_database}/{current_collection}', 'select all', 'select all')
            else:
                linked_stages.move_select_all(
                    f"{current_database}/{current_collection}",linked_stages)
            return True
        except Exception as e:
            print(
                RED + f"\nERROR : Unable to select all document from collection {current_collection} because of error - {e}"+RESET) if show_logs == True else None
            return False
    else:
        print(RED + "\nERROR : Invalid process of selecting all documents"+RESET)
        return False


def rename_field(command):
    try:
        if(db is not None and collection is not None):
            command = command.replace('rename', '').strip()
            field_pair = command.split(' and ')
            for pair in field_pair:
                pair_parts = pair.split(' eq ')
                pair_parts = [parts.strip() for parts in pair_parts]
                old_field_name, new_field_name = pair_parts[0], pair_parts[1]
                not_found_ids = []
                not_found_count = 0
                found_count = 0

                checked_ids = []
                bulk_operations = []
                for ids in selected_docs_id:
                    try:
                        update_criteria = {'_id': ids,
                                           old_field_name: {'$exists': True}}
                        document_field = collection.find_one(update_criteria)
                        if document_field:
                            update_query = UpdateOne(
                                {'_id': ids}, {'$rename': {old_field_name: new_field_name}})
                            bulk_operations.append(update_query)
                            if(ids not in checked_ids):
                                found_count += 1
                                checked_ids.append(ids)
                        else:
                            if(ids not in not_found_ids):
                                not_found_ids.append(ids)
                                checked_ids.append(ids)
                                not_found_count += 1
                    except Exception as e:
                        if(ids not in not_found_ids):
                            not_found_ids.append(ids)
                            checked_ids.append(ids)
                            not_found_count += 1

                if(bulk_operations):
                    collection.bulk_write(bulk_operations)

                print(
                    GREEN + f"\nSuccessfully renamed {old_field_name} to {new_field_name}" + RESET)

                return True

        else:
            print(RED + "ERROR:Invalid process of renaming field "+RESET)
            return False
    except Exception as e:
        print(
            RED + "ERROR: Any error accured or you may have entered invalid command."+RESET)
        return False


filter_operation = {
    'edit': lambda command: edit_selected_documents(command, False),
    'delete': lambda remove_message: delete_selected(remove_message, 'filter'),
    'add': lambda command: add_fields(command, False, 'filter'),
    'remove': lambda command: remove_field(command, False),
    'count': count,
    'append': lambda command: append_in_arr_field(command, 'filter'),
    'pop': lambda command: pop_from_arr_field(command, 'filter'),
    'rename': lambda command: rename_field(command)
}


def extract_value_from_filter(command, filter_type='eq') -> str:
    operators = {
        'eq': '$eq',
        'ne': '$ne',
        'gt': '$gt',
        'lt': '$lt',
        'gte': '$gte',
        'lte': '$lte',
        'in': '$in',
        'nin': '$nin',
        'regex': '$regex',
        'or': '$or',
        'contains': '$search',
        'task': '$task',
    }

    operator_pattern = '|'.join(re.escape(op) for op in operators.keys())

    if filter_type == 'eq':
        pattern = r'eq\s+(.*?)\s+(?={})'.format(operator_pattern)
    elif filter_type == 'in':
        pattern = r'in\s+(.*?)\s+(?={})'.format(operator_pattern)

    match = re.search(pattern, command)
    if match:
        # Extract the part between 'eq' or 'in' and the next operator
        extracted_part = match.group(1)
        return extracted_part.strip()
    else:
        return command


def filter_document(command, text_to_replace):
    global globally_selected_docs
    global selected_docs_id
    try:
        if(db is not None and collection is not None):
            command = command.replace(text_to_replace, '')
            filter_task = command.split(' task ')
            filter_operations = command.split(' and ') if len(
                filter_task) < 2 else filter_task[0].split(' and ')
            filter_operations = [operations.strip()
                                 for operations in filter_operations]
            filter_task = [task.strip() for task in filter_task]
            filter_task_operation = filter_task[0].split(' ')

            filter_query = {}
            operators = {
                'eq': '$eq',
                'ne': '$ne',
                'gt': '$gt',
                'lt': '$lt',
                'gte': '$gte',
                'lte': '$lte',
                'in': '$in',
                'nin': '$nin',
                'regex': '$regex',
                'or': '$or',
                'contains': '$search'
            }
            or_filter = []
            for filter in filter_operations:
                filter_parts = filter.split(' ')
                key, operator, value = filter_parts[0], filter_parts[1], extract_value_from_filter(
                    ' '.join(filter_task_operation[2:] if len(filter_task) > 1 else filter_parts[2:]).strip())
                value = process_value(value)
                operator = operators.get(operator, operator)
                if(operator == '$in'):
                    key, value = value, key
                    field_type = collection.find_one({key: {'$exists': True}})
                    if field_type and isinstance(field_type.get(key), list):
                        all_values = value.split(',')
                        all_values = [values.strip() for values in all_values]
                        processed_values = []
                        for val in all_values:
                            val = process_value(val)
                            processed_values.append(val)
                        filter_query[key] = {operator: [
                            v for v in processed_values]}

                    else:
                        print(RED + f"\nField {key} is not an array"+RESET)
                        return False

                elif operator in ['$gt', '$lt', '$gte', '$lte']:
                    field_type = collection.find_one(
                        {key: {'$exists': True}})

                    if field_type and isinstance(field_type.get(key), (int, float)):
                        filter_query[key] = {operator: float(value)}
                    else:
                        print(
                            RED + f"\nField '{key}' is not an integer or numeric" + RESET)
                        return False

                elif 'or' in filter_parts:
                    or_checking_values = filter.split(' or ')
                    or_checking_values = [v.strip()
                                          for v in or_checking_values]
                    logical_filter_processed = []
                    for values in or_checking_values:
                        print(values)
                        value_parts = values.split(' ')
                        print(value_parts)
                        logical_operator = operators.get(
                            value_parts[1], value_parts[1])
                        if logical_operator == '$eq':
                            logical_filter_processed.append({
                                value_parts[0]: ' '.join(value_parts[2:])})
                        elif logical_operator == '$in':
                            logical_filter_processed.append({
                                value_parts[2]: {
                                    '$exists': value_parts[0]
                                }
                            })
                        else:
                            logical_filter_processed.append({
                                value_parts[0]: {
                                    logical_operator: ' '.join(value_parts[2:])}
                            })
                    or_filter.extend(logical_filter_processed)

                elif operator == '$search':
                    value, key = key, value
                    filter_query[value] = {'$regex': key, '$options': 'i'}

                else:
                    if(key == '_id' or key == 'id'):
                        filter_query['_id'] = {
                            operator: ObjectId(str(value))}
                    else:
                        filter_query[key] = {operator: value}

            if or_filter:
                filter_query['$or'] = or_filter
            filtered_docs = collection.find(filter_query)
            id_container = []
            to_show = True
            format_documents = []

            for doc in filtered_docs:
                if(to_show is True and text_to_replace == 'filter'):
                    print(GREEN + "\nFiltered docs are given below" +
                          RESET) if len(filter_task) <= 1 else None
                to_show = False

                formatted_doc = format_document(doc)
                format_documents.append(formatted_doc)
                id_container.append(doc['_id'])
                if(text_to_replace == 'filter'):
                    print(PURPLE + "\n" + formatted_doc +
                          RESET) if len(filter_task) <= 1 else None

            if to_show is True:
                print(RED + "\nNo documents found with the given filter" +
                      RESET) if text_to_replace == 'filter' else None
                return False if text_to_replace == 'filter' else id_container

            if len(filter_task) > 1:
                selected_docs_id.clear()
                selected_docs_id.extend(id_container)
                filter_operations = [operations.strip()
                                     for operations in filter_task]
                filter_operations.pop(0)
                for operations in filter_operations:
                    operation_parts = operations.split(' ')
                    operation_process = operation_parts[0]
                    if type(operation_parts[0]) == str:
                        if operation_process in filter_operation:
                            if operation_process == 'delete':
                                filter_operation[operation_process](
                                    'do not show')
                            else:
                                filter_operation[operation_process](operations)
                        else:
                            print(
                                RED + "\nERROR: Invalid operation command." + RESET)
                            return False
                remove_selection('do not show')
            return format_documents if text_to_replace == 'filter' else id_container

        else:
            print(RED + '\nERROR : Process of filtering document is invalid')
            return False
    except Exception as e:
        print(RED + "\nERORR : Any internal error accured or you may have entered invalid command."+RESET)
        return False


def go_back():
    global current_collection, current_database
    global collection, db
    global not_to_move_back, stage_moved
    previous_stage = linked_stages.current_stage.prev

    if(len(selected_docs_id) > 0 and len(globally_selected_docs) > 0):
        selected_docs_id.clear()
        globally_selected_docs.clear()

    if(previous_stage == None):
        print(YELLOW + '\nAlready on the edge, nothing to move back on !' + RESET)
    else:
        if(previous_stage.stage_type == 'home'):
            linked_stages.move_stage_back(linked_stages)
            navigate_home('do not show')
        elif(previous_stage.stage_type == 'database'):
            database_name = previous_stage.stage
            enterInDatabase(database_name, 'checked')
            linked_stages.move_stage_back(linked_stages)
        elif(previous_stage.stage_type == 'collection'):
            collection_name = previous_stage.stage
            collection = previous_stage
            path = collection.path
            path_arr = path.split('/')
            path_arr = [p.strip() for p in path_arr]
            get_direct_access(path_arr[0], path_arr[1], False)
            linked_stages.move_stage_back(linked_stages)

        elif(previous_stage.stage_type == 'document'):
            if(previous_stage.selection_type == 'filtered document'):
                linked_stages.move_stage_back(linked_stages)
                select_document(
                    f'select {linked_stages.current_stage.filter}', False, False)
            elif(previous_stage.selection_type == 'searched document'):
                linked_stages.move_stage_back(linked_stages)
                path = linked_stages.current_stage.path.split('/')
                path = [p.strip() for p in path]
                db_name, collection_name = path[0], path[1]
                enterInDatabase(db_name, 'checked') if current_database.lower(
                ) != db_name.lower() else None
                enterInCollection(collection_name, 'checked') if current_collection.lower(
                ) != collection_name.lower() else None
                search_text(
                    f'search {linked_stages.current_stage.filter.strip()}')

            elif(previous_stage.selection_type == 'select all'):
                linked_stages.move_stage_back(linked_stages)
                path = linked_stages.current_stage.path.split('/')
                path = [p.strip() for p in path]
                enterInDatabase(path[0].lower()) if path[0].lower(
                ) == current_collection.lower() else None
                enterInCollection(path[1].lower()) if path[1].lower(
                ) == current_database.lower() else None
                select_all(False)

        print(GREEN + '\nStage Updated' + RESET)

    return True


def go_next():
    current_stage = linked_stages.current_stage
    next = current_stage.next
    if(len(selected_docs_id) > 0 and len(globally_selected_docs) > 0):
        selected_docs_id.clear()
        globally_selected_docs.clear()

    if(current_stage.next is not None):
        if next.stage_type == 'database':
            database_name = next.stage
            enterInDatabase(database_name, 'not checked')
            linked_stages.move_stage_forward(linked_stages)
            print('moved forward')
        elif(next.stage_type == 'collection'):
            collection_path_full = next.path
            collection_path_splitted = collection_path_full.split('/')
            collection_path_splitted = [path.strip()
                                        for path in collection_path_splitted]
            db_name = collection_path_splitted[0]
            collection_name = collection_path_splitted[1]
            get_direct_access(db_name, collection_name, False)
            linked_stages.move_stage_forward(linked_stages)

        elif(next.stage_type == 'document'):
            if(next.selection_type == 'filtered document'):
                linked_stages.move_stage_forward(linked_stages)
                select_document(
                    f'select {linked_stages.current_stage.filter}', False, False)
            elif(next.selection_type == 'searched document'):
                linked_stages.move_stage_forward(linked_stages)
                path = linked_stages.current_stage.path.split('/')
                path = [p.strip() for p in path]
                db_name, collection_name = path[0], path[1]
                enterInDatabase(db_name, 'checked') if current_database.lower(
                ) != db_name.lower() else None
                enterInCollection(collection_name, 'checked') if current_collection.lower(
                ) != collection_name.lower() else None
                search_text(
                    f'search {linked_stages.current_stage.filter.strip()}')

            elif(next.selection_type == 'select all'):
                linked_stages.move_stage_forward(linked_stages)
                path = linked_stages.current_stage.path.split('/')
                path = [p.strip() for p in path]
                enterInDatabase(path[0].lower()) if path[0].lower(
                ) == current_collection.lower() else None
                enterInCollection(path[1].lower()) if path[1].lower(
                ) == current_database.lower() else None
                select_all(False)

        print(GREEN + "\nStage Updated"+RESET)
        return True
    else:
        print(YELLOW + '\nAlready on the last stage, nowhere to go from here !'+RESET)
        return False


def set_identifier():
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
            identifier_count = 1
            last_identifier_value = None
            for doc in globally_selected_docs:
                if 'identifier' not in doc:
                    if(last_identifier_value is not None):
                        doc['identifier'] = last_identifier_value
                    else:
                        doc['identifier'] = identifier_count
                else:
                    last_identifier_value = doc['identifer']
            collection.bulk_write(
                [pymongo.ReplaceOne({"_id": doc["_id"]}, doc) for doc in globally_selected_docs])
            print(
                GREEN + "\nSuccessfully added identifiers to all selected dcouments" + RESET)
            return True
    else:
        print(RED + "ERROR : Invalid process of adding identifiers")
        return True


def remove_identifier():
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


def get_recent_port():
    try:
        with open("config.yaml", "r") as f:
            data = yaml.safe_load(f)
            if(data == None):
                return None

            return data.get("recent_port")
    except (FileNotFoundError, yaml.YAMLError):
        return None


def save_port(port):
    try:
        data = {'recent_port': int(port)}
        with open('config.yaml', "w") as f:
            yaml.dump(data, f)
            return True
    except (FileNotFoundError):
        return False


def remove_port():
    try:
        key = 'recent_port'
        with open('config.yaml', 'r') as f:
            data = yaml.load(f)
            if(data is None):
                print(YELLOW+"\nRecent port not found"+RESET)
                return True
        if data is not None and key in data:
            del data[key]

        with open('config.yaml', 'w') as f:
            yaml.dump(data, f)

        print(GREEN + '\nRemoved the recent port, restarting the process...'+RESET)
        main()
        return True

    except (FileNotFoundError):
        create_config_yaml()
        print(GREEN + '\nRemoved recent port successfully'+RESET)
        return True


def start_service():
    if boolStatus is False and mongoStatus == 'Stopped':
        start = start_mongodb_service()
        if start['type'] == 'success':
            boolStatus = status.check_mongo_status()
            mongoStatus = 'Running'
        showStatus()
    else:
        print(YELLOW + '\nMongoDB is already up and running' + RESET)


def stop_service():
    if boolStatus is True and mongoStatus == 'Running':
        from mongodb_service_handler import stop_mongodb_service
        stop = stop_mongodb_service()
        if(stop['type'] == 'success'):
            boolStatus = status.check_mongo_status()
            mongoStatus = 'Stopped'
        showStatus()
    else:
        print(YELLOW + '\nMongoDB is already stopped' + RESET)


def restart_service():
    from mongodb_service_handler import restart_mongodb_service
    restart = restart_mongodb_service()
    if restart['type'] == 'success':
        boolStatus == status.check_mongo_status()
        mongoStatus = 'Running'
    showStatus()


global_commands = {
    'start mongo': start_service,
    'stop mongo': stop_service,
    'restart mongo': restart_service,
}

client = None


def connect(port):
    global client
    try:
        client = MongoClient(f"mongodb://localhost:{port}")
        return True
    except Exception as e:
        print(RED + "\nUnable to connect with mongodb, try again!" + RESET)
        return False


boolStatus = status.check_mongo_status()
mongoStatus = 'Running' if boolStatus == True else "Stopped"

showStatus()

commands = {
    'status': showStatus,
    'start mongo': start_service,
    'stop mongo': stop_service,
    'restart mongo': restart_service,
    'show dbs': showDB,
    'show database': showDB,
    'show databases': showDB,
    'choose db': chooseDB,
    'restart': restart_executer,
    'show collections': show_collections,
    'choose collection': choose_collection,
    'errors': show_errors,
    'info': get_info,
    'read all': get_collection_data,
    'delete all': delete_documents,
    'home': navigate_home,
    'show selected': show_selected,
    'back': go_back,
    'go back': go_back,
    'next': go_next,
    'forward': go_next,
    'go next': go_next,
    'remove selection': remove_selection,
    'delete selected': delete_selected,
    'select all': select_all,
    'set identifier': set_identifier,
    'set identifiers': set_identifier,
    'remove identifier': remove_identifier,
    'remove identifiers': remove_identifier,
    'status': showStatus
}


def check_mongo_running(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(('localhost', port))
        return True
    except ConnectionRefusedError:
        return False
    except socket.timeout:
        return False


def main():
    global boolStatus
    global mongoStatus

    try:
        recent_port = get_recent_port()
        while True:
            if recent_port is not None:
                connect(recent_port)
                command = input(BLUE + f'\n{currentURI} ' + RESET)

                if command.lower() == 'exit' or command.lower() == 'close':
                    sys.exit()
                elif command.lower() == 'start mongo':
                    start_service()

                elif command.lower() == 'stop mongo':
                    stop_service()
                elif command.lower() == 'restart mongo':
                    restart_service()
                elif command.lower() == 'restart':
                    restart_executer()
                elif boolStatus is True:
                    parseCommand(command.strip())
                else:
                    if command not in global_commands:
                        print(
                            RED + '\nERROR - MongoDB is not running, please run "start mongo" command to get connected with local MongoDB' + RESET)
            else:
                command = input(
                    BLUE + f'\nPort on which MongoDB is running > ' + RESET)
                if command.isdigit():
                    running = check_mongo_running(int(command))
                    if running:
                        print(
                            GREEN + '\nSuccessfully connected to the MongoDB, port is saved as default to change the port use command "change port {port name}"' + RESET)
                        save_port(int(command))
                    else:
                        print(
                            RED + "\nFailed to connect, because MongoDB is not running on the given port")
                else:
                    print(RED + "\nGiven port name is invalid!" + RESET)

    except KeyboardInterrupt:
        sys.exit()


if __name__ == '__main__':
    main()


# --------------------------------------------------BUGS--------------------------------------------------------------
# BUG  - can't filter when filter command contains in and or both
# * BUG - 1. Selection gets removed when we add new field when the selection is on the basis of search
# * BUG - 2. Can't select document when filter contains array
# * BUG - Filter can't give accurate results when filter contains arr
# * BUG - Can't add more then two item of object using append command
# * BUG - TypeError: Object of type datetime is not JSON serializable
