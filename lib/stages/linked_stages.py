import sys,os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append(os.path.join(SCRIPT_DIR, 'stage_operations'))
from stage_operations.operations import *
from stage_operations.existence import *
from stage_operations.current_stage_handler import *
from stage_node import Stage

class LinkedStages(object):
    def __init__(self):
        stage = Stage(None, None)
        self.head = stage
        self.tail = stage
        self.length = 1
        self.current_stage = stage

    def add_stage(self, linked_stage, stage_name, stage_type, path=None, filter=None, selection_type=None):
        add_stage_to_linked_stages(linked_stage, stage_name, stage_type, path, filter, selection_type)

    def clear_stage(self, stage_list):
        clear_stages(stage_list)

    def remove_current_stage(self, stage_list):
        return remove_current_stage(stage_list)

    def print_stages(self, stage_list):
        print_stages(stage_list)

    def get_current_stage(self, stage_list):
        return get_current_stage(stage_list)

    def do_stage_exists(self, stage, stage_list):
        return do_stage_exists(stage_list, stage)

    def do_select_all_exists(self, path, stage_list):
        return do_select_all_exists(stage_list, path)

    def move_to_existing_stage(self, stage, stage_list):
        return move_to_existing_stage(stage_list, stage)

    def move_select_all(self, path, stage_list):
        return move_select_all(stage_list, path)

    def move_stage_back(self, stage_list):
        return move_stage_back(stage_list)

    def move_stage_forward(self, stage_list):
        return move_stage_forward(stage_list)


