import sys
import os
from stage_node import Stage

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


def add_stage_to_linked_stages(linked_stages, stage_name, stage_type, path=None, filter=None, selection_type=None):
    new_stage = Stage(stage_name, stage_type, path, selection_type, None, None, filter)
    if linked_stages.length == 1:
        linked_stages.head = new_stage
        linked_stages.tail = new_stage
    else:
        if linked_stages.current_stage.next is not None:
            new_stage.next = linked_stages.current_stage.next
            new_stage.prev = linked_stages.current_stage
            linked_stages.current_stage.next = new_stage
            linked_stages.current_stage = new_stage
        else:
            linked_stages.tail.next = new_stage
            new_stage.prev = linked_stages.tail
            linked_stages.tail = new_stage
    linked_stages.filter = filter
    linked_stages.length += 1
    linked_stages.current_stage = new_stage
    return True


def clear_stages(linked_stages):
    temp = linked_stages.head
    while temp:
        current = temp.next
        del current
        current = temp.next
        temp = temp.next
    linked_stages.head = None
    return True


def remove_current_stage(linked_stages):
    if linked_stages.length == 0:
        return False
    elif linked_stages.length == 1:
        linked_stages.head = None
        linked_stages.tail = None
        linked_stages.current_stage = None
        return True
    else:
        temp = linked_stages.tail
        linked_stages.tail = linked_stages.tail.prev
        linked_stages.tail.next = None
        temp.prev = None
        linked_stages.current_stage = linked_stages.tail
        return True


def print_stages(linked_stages):
    temp = linked_stages.head
    while temp is not None:
        print({'stage name': temp.stage, 'stage type': temp.stage_type,
               'stage path': temp.path if temp.path is not None else 'Not available', 'stage filter': temp.filter if temp.filter is not None else 'Not Available', 'selection type': temp.selection_type if temp.selection_type is not None else 'Not Available'})
        temp = temp.next
