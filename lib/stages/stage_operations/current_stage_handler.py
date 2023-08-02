import sys,os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from stage_node import Stage

def get_current_stage(linked_stages):
    if linked_stages.current_stage is not None:
        return {'stage_name':linked_stages.current_stage.stage,'stage_type':linked_stages.current_stage.stage_type}
    else:
        return False
    
    
def move_to_existing_stage(linked_stages, stage):
    stage_to_find = None
    stage = stage.strip() if stage is not None else None
    temp = linked_stages.head
    while temp:
        if temp.stage == stage:
            stage_to_find = temp
            break
        else:
            temp = temp.next
    if stage_to_find is not None:
        linked_stages.current_stage = stage_to_find
        return True
    else:
        return False

def move_select_all(linked_stages, path):
    stage_to_find = None
    path = path.strip() if path is not None else None
    temp = linked_stages.head
    while temp:
        if temp.selection_type == 'select all':
            if temp.path.strip() == path:
                stage_to_find = temp
                break
        temp = temp.next
    linked_stages.current_stage = stage_to_find
    return True

def move_stage_back(linked_stages):
    if linked_stages.length == 0:
        return False
    if linked_stages.length > 1 and linked_stages.current_stage != linked_stages.head:
        linked_stages.current_stage = linked_stages.current_stage.prev
        return True
    else:
        return False

def move_stage_forward(linked_stages):
    if linked_stages.length == 0:
        return False
    if linked_stages.length > 1 and linked_stages.current_stage != linked_stages.tail:
        linked_stages.current_stage = linked_stages.current_stage.next
        return True
    else:
        return False
