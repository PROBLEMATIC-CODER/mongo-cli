class Stage(object):
    def __init__(self, stage, stage_type, path=None, selection_type=None, next=None, prev=None, filter=None):
        self.stage = stage
        self.stage_type = stage_type
        self.path = path
        self.filter = filter
        self.next = next
        self.prev = prev
        self.selection_type = selection_type


class LinkedStages(object):
    def __init__(self):
        stage = Stage(None, None)
        self.head = stage
        self.tail = stage
        self.length = 1
        self.current_stage = stage

    def add_stage(self, stage_name, stage_type, path=None, filter=None, selection_type=None):
        new_stage = Stage(stage_name, stage_type, path,
                          selection_type, None, None, filter)
        if(self.length == 1):
            self.head = new_stage
            self.tail = new_stage
        else:
            if(self.current_stage.next is not None):
                new_stage.next = self.current_stage.next
                new_stage.prev = self.current_stage
                self.current_stage.next = new_stage
                self.current_stage = new_stage
            else:
                self.tail.next = new_stage
                new_stage.prev = self.tail
                self.tail = new_stage
        self.filter = filter
        self.length += 1
        self.current_stage = new_stage
        return True

    def clear_stage(self):
        temp = self.head
        while temp:
            current = temp.next
            del current
            current = temp.next
        self.head = None
        return True

    def remove_current_stage(self):
        if self.length == 0:
            return False
        elif self.length == 1:
            self.head = None
            self.tail = None
            self.current_stage = None
            return True
        else:
            temp = self.tail
            self.tail = self.tail.prev
            self.tail.next = None
            temp.prev = None
            self.current_stage = self.tail
            return True

    def print_stages(self):
        temp = self.head
        while temp is not None:
            print({'stage name': temp.stage, 'stage type': temp.stage_type,
                  'stage path': temp.path if temp.path is not None else 'Not available', 'stage filter': temp.filter if temp.filter is not None else 'Not Available', 'selection type': temp.selection_type if temp.selection_type is not None else 'Not Available'})
            temp = temp.next

    def get_current_stage(self):
        if(self.current_stage is not None):
            return self.current_stage
        else:
            return False

    def do_stage_exists(self, stage):
        temp = self.head

        while temp:
            if(temp.stage == stage):
                return True
            temp = temp.next
        return False

    def do_select_all_exists(self, path):
        temp = self.head
        while temp:
            if(temp.selection_type == 'select all'):
                if(temp.path == path):
                    return True
            temp = temp.next
        return False

    def move_to_existing_stage(self, stage):
        stage_to_find = None
        stage = stage.strip() if stage is not None else None
        temp = self.head

        while temp:
            if temp.stage == stage:
                stage_to_find = temp
                break
            else:
                temp = temp.next
        if(stage_to_find is not None):
            self.current_stage = stage_to_find
            return True
        else:
            return False

    def move_select_all(self, path):
        stage_to_find = None
        path = path.strip() if path is not None else None
        temp = self.head
        while temp:
            if(temp.selection_type == 'select all'):
                if(temp.path.strip() == path):
                    stage_to_find = temp
                    break
            temp = temp.next
        self.current_stage = stage_to_find
        return True

    def move_stage_back(self):
        if self.length == 0:
            return False
        if(self.length > 1 and self.current_stage != self.head):
            self.current_stage = self.current_stage.prev
            return True
        else:
            return False

    def move_stage_forward(self):
        if self.length == 0:
            return False
        if(self.length > 1 and self.current_stage != self.tail):
            self.current_stage = self.current_stage.next
            return True
        else:
            return False
