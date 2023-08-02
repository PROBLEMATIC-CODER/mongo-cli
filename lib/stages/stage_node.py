class Stage(object):
    def __init__(self, stage, stage_type, path=None, selection_type=None, next=None, prev=None, filter=None):
        self.stage = stage
        self.stage_type = stage_type
        self.path = path
        self.filter = filter
        self.next = next
        self.prev = prev
        self.selection_type = selection_type

