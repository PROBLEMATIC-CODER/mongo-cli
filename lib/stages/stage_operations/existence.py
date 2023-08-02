import sys,os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from stage_node import Stage


def do_stage_exists(linked_stages, stage):
    temp = linked_stages.head
    while temp:
        if temp.stage == stage:
            return True
        temp = temp.next
    return False

def do_select_all_exists(linked_stages, path):
    temp = linked_stages.head
    while temp:
        if temp.selection_type == 'select all':
            if temp.path == path:
                return True
        temp = temp.next
    return False



    

