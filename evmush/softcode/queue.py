from evmush.models import MushObject


class ActionQueue:
    def __init__(self):
        self.queue = list()
        self.pid_dict = dict()
        self.pid = 0


class QueueEntry:

    def __init__(self, pid: int, enactor: MushObject, executor: MushObject, actions: str):
        self.pid = pid
        self.enactor = enactor
        self.executor = executor
        self.actions = actions


class FunctionCall:

    def __init__(self, enactor: MushObject, executor: MushObject, func):
        self.enactor = enactor
        self.executor = executor
        self.func = func