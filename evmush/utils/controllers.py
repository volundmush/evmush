from django.conf import settings

from evennia.utils.logger import log_trace
from evennia.utils.utils import class_from_module
from athanor.utils.online import admin_accounts


class ControllerManager:

    def __init__(self):
        self.loaded = False
        self.controllers = dict()

    def load(self):
        for controller_key, controller_def in settings.CONTROLLERS.items():
            con_class = class_from_module(controller_def.get("class", settings.BASE_CONTROLLER_CLASS))
            backend = class_from_module(controller_def.get('backend'))
            self.controllers[controller_key] = con_class(controller_key, self, backend)
        self.loaded = True

    def get(self, con_key):
        if not self.loaded:
            self.load()
        if not (found := self.controllers.get(con_key, None)):
            raise ValueError("Controller not found!")
        if not found.loaded:
            found.load()
        return found


class AthanorController:
    system_name = None

    def __init__(self, key, manager, backend):
        self.key = key
        self.manager = manager
        self.loaded = False
        self.backend = backend(self)

    def alert(self, message, enactor=None):
        for acc in admin_accounts():
            acc.system_msg(message, system_name=self.system_name, enactor=enactor)

    def msg_target(self, message, target):
        target.msg(message, system_alert=self.system_name)

    def load(self):
        """
        This is a wrapper around do_load that prevents it from being called twice.

        Returns:
            None
        """
        if self.loaded:
            return
        self.do_load()
        self.loaded = True

    def do_load(self):
        """
        Implements the actual logic of loading. Meant to be overloaded.
        """
        pass


class AthanorControllerBackend:
    typeclass_defs = list()

    def __init__(self, frontend):
        self.frontend = frontend
        self.system_name = frontend.system_name
        self.loaded = False

    def alert(self, message, enactor=None):
        for acc in admin_accounts():
            acc.system_msg(message, system_name=self.system_name, enactor=enactor)

    def msg_target(self, message, target):
        target.msg(message, system_alert=self.system_name)

    def load_typeclasses(self):
        for tcdef in self.typeclass_defs:
            try:
                setattr(self, tcdef[0], class_from_module(getattr(settings, tcdef[1]),
                                                          defaultpaths=settings.TYPECLASS_PATHS))
            except Exception:
                log_trace()
                setattr(self, tcdef[0], tcdef[2])

    def load(self):
        """
        This is a wrapper around do_load that prevents it from being called twice.

        Returns:
            None
        """
        if self.loaded:
            return
        self.load_typeclasses()
        self.do_load()
        self.loaded = True

    def do_load(self):
        """
        Implements the actual logic of loading. Meant to be overloaded.
        """
        pass
