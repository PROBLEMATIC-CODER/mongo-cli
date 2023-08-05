import os

import sys
from pymongo import InsertOne
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.dirname(SCRIPT_DIR))

sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'utils'))
sys.path.append(os.path.join(SCRIPT_DIR, 'lib', 'operation_helpers'))
from utils.text_colors import RESET,GREEN,PURPLE,YELLOW

def get_selected_value(command,globally_selected_docs):
    if (len(globally_selected_docs) != 0):
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
    else:
        print(YELLOW + "\nSelect documents to perform this operations."+RESET)
        return False

