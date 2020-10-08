from django.conf import settings
from evennia.utils import utils


class ExamineHandler:
    """
    Simple lazy-property class for handling all 'examine' generation.
    """

    examine_type = None
    examine_caller_type = None

    def __init__(self, obj):
        self.obj.obj = obj

    def render_examine_identifier(self, viewer):
        dbclass = f"({self.obj.dbtype}: {self.obj.dbref}) " if hasattr(self, 'dbtype') else None
        return f"{dbclass if dbclass else ''}{self.obj.examine_type}: {self.obj.get_display_name(viewer)}"

    def render_examine_callback(self, cmdset, viewer, callback=True):
        styling = viewer.styler
        message = list()
        message.append(
            styling.styled_header(f"Examining {self.obj.render_examine_identifier(viewer)}"))
        try:
            for hook in settings.EXAMINE_HOOKS[self.obj.examine_type]:
                hook_call = f"render_examine_{hook}"
                if hasattr(self, hook_call):
                    message.extend(getattr(self, hook_call)(viewer, cmdset, styling))
        except Exception as e:
            viewer.msg(e)
        message.append(styling.blank_footer)
        rendered = '\n'.join(str(l) for l in message)
        if not callback:
            return rendered
        viewer.msg(rendered)

    def render_examine(self, viewer, callback=True):
        obj_session = self.obj.sessions.get()[0] if self.obj.sessions.count() else None
        get_and_merge_cmdsets(
            self, obj_session, None, None, self.obj.examine_caller_type, "examine"
        ).addCallback(self.obj.get_cmdset_callback, viewer)

    def render_examine_commands(self, viewer, avail_cmdset, styling):
        if not (len(self.obj.cmdset.all()) == 1 and self.obj.cmdset.current.key == "_EMPTY_CMDSET"):
            # all() returns a 'stack', so make a copy to sort.
            stored_cmdsets = sorted(self.obj.cmdset.all(), key=lambda x: x.priority, reverse=True)
            string = "|wStored Cmdset(s)|n:\n %s" % (
                "\n ".join(
                    "%s [%s] (%s, prio %s)"
                    % (cmdset.path, cmdset.key, cmdset.mergetype, cmdset.priority)
                    for cmdset in stored_cmdsets
                    if cmdset.key != "_EMPTY_CMDSET"
                )
            )

            # this gets all components of the currently merged set
            all_cmdsets = [(cmdset.key, cmdset) for cmdset in avail_cmdset.merged_from]
            # we always at least try to add account- and session sets since these are ignored
            # if we merge on the object level.
            if hasattr(self, "account") and self.obj.account:
                all_cmdsets.extend([(cmdset.key, cmdset) for cmdset in self.obj.account.cmdset.all()])
                if self.obj.sessions.count():
                    # if there are more sessions than one on objects it's because of multisession mode 3.
                    # we only show the first session's cmdset here (it is -in principle- possible that
                    # different sessions have different cmdsets but for admins who want such madness
                    # it is better that they overload with their own CmdExamine to handle it).
                    all_cmdsets.extend(
                        [
                            (cmdset.key, cmdset)
                            for cmdset in self.obj.account.sessions.all()[0].cmdset.all()
                        ]
                    )
            else:
                try:
                    # we have to protect this since many objects don't have sessions.
                    all_cmdsets.extend(
                        [
                            (cmdset.key, cmdset)
                            for cmdset in self.obj.get_session(self.obj.sessions.get()).cmdset.all()
                        ]
                    )
                except (TypeError, AttributeError):
                    # an error means we are merging an object without a session
                    pass
            all_cmdsets = [cmdset for cmdset in dict(all_cmdsets).values()]
            all_cmdsets.sort(key=lambda x: x.priority, reverse=True)
            string += "\n|wMerged Cmdset(s)|n:\n %s" % (
                "\n ".join(
                    "%s [%s] (%s, prio %s)"
                    % (cmdset.path, cmdset.key, cmdset.mergetype, cmdset.priority)
                    for cmdset in all_cmdsets
                )
            )

            # list the commands available to this object
            avail_cmdset = sorted([cmd.key for cmd in avail_cmdset if cmd.access(self, "cmd")])

            cmdsetstr = utils.fill(", ".join(avail_cmdset), indent=2)
            string += "\n|wCommands available to %s (result of Merged CmdSets)|n:\n %s" % (
                self.obj.key,
                cmdsetstr,
            )
            return [
                styling.styled_separator("Commands"),
                string
            ] if string else []

    def render_examine_nattributes(self, viewer, cmdset, styling):
        return list()

    def render_examine_attributes(self, viewer, cmdset, styling):
        return list()

    def render_examine_tags(self, viewer, cmdset, styling):
        tags_string = utils.fill(
            ", ".join(
                "%s[%s]" % (tag, category)
                for tag, category in self.obj.tags.all(return_key_and_category=True)
            ),
            indent=5,
        )
        if tags_string:
            return [f"|wTags[category]|n: {tags_string.strip()}"]
        return list()


class AccountExamineHandler(ExamineHandler):
    examine_type = "account"
    examine_caller_type = "account"

    def render_examine(self, viewer, callback=True):
        obj_session = self.obj.sessions.get()[0] if self.obj.sessions.count() else None
        get_and_merge_cmdsets(
            self, obj_session, self, None, self.obj.examine_type, "examine"
        ).addCallback(self.obj.render_examine_callback, viewer)

    def render_examine_account(self, viewer, cmdset, styling):
        message = list()
        message.append(f"|wUsername|n: |c{self.obj.name}|n ({self.obj.dbref})")
        message.append(f"|wTypeclass|n: {self.obj.typename} ({self.obj.typeclass_path})")
        if (aliases := self.obj.aliases.all()):
            message.append(f"|wAliases|n: {', '.join(utils.make_iter(str(aliases)))}")
        if (sessions := self.obj.sessions.all()):
            message.append(f"|wSessions|n: {', '.join(str(sess) for sess in sessions)}")
        message.append(f"|wEmail|n: {self.obj.email}")
        if (characters := self.obj.characters()):
            message.append(f"|wCharacters|n: {', '.join(str(l) for l in characters)}")
        return message

    def render_examine_access(self, viewer, cmdset, styling):
        locks = str(self.obj.locks)
        if locks:
            locks_string = utils.fill("; ".join([lock for lock in locks.split(";")]), indent=6)
        else:
            locks_string = " Default"
        message = [
            styling.styled_separator("Access"),
            f"|wPermissions|n: {', '.join(perms) if (perms := self.obj.permissions.all()) else '<None>'}",
            f"|wSuperuser|n: {self.obj.is_superuser}",
            f"|wLocks|n:{locks_string}"
        ]
        return message

    def render_examine_puppets(self, viewer, cmdset, styling):
        return list()

    def render_examine_puppeteer(self, viewer, cmdset, styling):
        message = [
            styling.styled_separator("Connected Account"),
            f"|wUsername|n: {self.obj.username}",
            f"|wEmail|n: {self.obj.email}",
            f"|wTypeclass|n: {self.obj.typename} ({self.obj.typeclass_path})",
            f"|wPermissions|n: {', '.join(perms) if (perms := self.obj.permissions.all()) else '<None>'} (Superuser: {self.obj.is_superuser}) (Quelled: {bool(self.obj.db._quell)})",
            f"|wOperations|n: {', '.join(opers) if (opers := self.obj.operations.all()) else '<None>'}",
            f"|wSessions|n: {', '.join(str(sess) for sess in self.obj.sessions.all())}"
        ]
        return message


class ObjectExamineHandler(ExamineHandler):
    examine_type = "object"
    examine_caller_type = 'object'

    def render_examine(self, viewer):
        obj_session = self.obj.sessions.get()[0] if self.obj.sessions.count() else None
        get_and_merge_cmdsets(
            self, obj_session, self.obj.account, self, self.obj.examine_caller_type, "examine"
        ).addCallback(self.obj.render_examine_callback, viewer)

    def render_examine_object(self, viewer, cmdset, styling, type_name="Object"):
        message = [
            styling.styled_separator(f"{type_name} Properties"),
            f"|wName/key|n: |c{self.obj.key}|n ({self.obj.dbref})",
            f"|wTypeclass|n: {self.obj.typename} ({self.obj.typeclass_path})"
        ]
        if (aliases := self.obj.aliases.all()):
            message.append(f"|wAliases|n: {', '.join(utils.make_iter(str(aliases)))}")
        if (sessions := self.obj.sessions.all()):
            message.append(f"|wSessions|n: {', '.join(str(sess) for sess in sessions)}")
        message.append(f"|wHome:|n {self.obj.home} ({self.obj.home.dbref if self.obj.home else None})")
        message.append(f"|wLocation:|n {self.obj.location} ({self.obj.location.dbref if self.obj.location else None})")
        if (destination := self.obj.destination):
            message.append(f"|wDestination|n: {destination} ({destination.dbref})")
        return message

    def render_examine_access(self, viewer, cmdset, styling):
        locks = str(self.obj.locks)
        if locks:
            locks_string = utils.fill("; ".join([lock for lock in locks.split(";")]), indent=6)
        else:
            locks_string = " Default"
        message = [
            styling.styled_separator("Access"),
            f"|wPermissions|n: {', '.join(perms) if (perms := self.obj.permissions.all()) else '<None>'}",
            f"|wLocks|n:{locks_string}"
        ]
        return message

    def render_examine_puppeteer(self, viewer, cmdset, styling):
        if not (account := self.obj.account):
            return list()
        return account.render_examine_puppeteer(viewer, cmdset, styling)

    def render_examine_scripts(self, viewer, cmdset, styling):
        if not (scripts := self.obj.scripts.all()):
            return list()
        message = [
            styling.styled_separator("Scripts"),
            scripts
        ]
        return message()

    def render_examine_contents(self, viewer, cmdset, styling):
        if not (contents_index := self.obj.contents_index):
            return list()
        message = list()
        for category, contents in contents_index.items():
            message.append(styling.styled_separator(f"Contents: {category.capitalize()}s"))
            message.append(', '.join([f'{t.name}({t.dbref})' for t in contents]))
        return message


class SessionExamineHandler(ExamineHandler):
    examine_hooks = ['session', 'puppet', 'commands', 'tags', 'attributes']
    examine_type = "session"

    def render_examine(self, viewer):
        pass

    def render_examine_session(self, viewer, cmdset, styling):
        message = list()
        message.append(f"|wAddress|n: |c{self.obj.address}|n")
        message.append(f"|wProtocol|n: {self.obj.protocol_key}")
        message.append(f"|wTypeclass|n: {self.obj.typename} ({self.obj.typeclass_path})")
        return message

    def render_examine_puppet(self, viewer, cmdset, styling):
        return list()


class ScriptExamineHandler(ExamineHandler):
    pass
