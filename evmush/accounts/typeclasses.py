from evennia.utils.utils import lazy_property
from evennia.accounts.accounts import DefaultAccount
from evennia.utils.utils import time_format

import athanor
from athanor.accounts.handlers import AccountCmdSetHandler
from athanor.accounts.handlers import BanHandler, AccountCmdHandler, AccountAppearanceHandler


class AthanorAccount(DefaultAccount):
    """
    AthanorAccount adds the EventEmitter to DefaultAccount and supports Mixins.
    Please read Evennia's documentation for its normal API.
    """
    # class properties used by the RenderExamine mixin.
    examine_type = "account"
    examine_caller_type = "account"
    dbtype = 'AccountDB'
    _cmd_sort = -1100

    @lazy_property
    def cmdset(self):
        return AccountCmdSetHandler(self, True)

    @lazy_property
    def cmd(self):
        return AccountCmdHandler(self)

    @lazy_property
    def ban(self):
        return BanHandler(self)

    def at_session_login(self, session):
        """
        Is called by the unlogged-in connect command for checking whether the player should be allowed to login.
        This should check for bans, disabled state, etc, and message the session about results.

        Args:
            session (ServerSession): The session attempting to connect.

        """
        # check for both if the account has been banned and whether the ban is still valid.
        # it's still valid if banned > now.
        if (bstate := self.ban.get_state()):
            session.msg(f"This account has been banned for: {bstate['reason']} until {bstate['until'].strftime('%c')}. "
                        f"{time_format(bstate['left'].total_seconds(), style=2)} remains. If you wish to appeal, contact staff via other means.")
            return

        # next check for if the account is disabled.
        if (disabled := self.db._disabled):
            session.msg(
                f"This account has been indefinitely disabled for the reason: {disabled}. If you wish to appeal,"
                f"contact staff via other means.")
            return

        # Did all go well? Then proceed with login and display the select screen.
        session.login(self)
        session.msg(self.return_appearance(session))

    def set_email(self, new_email):
        """
        Validates and normalizes email, then sets it.

        No permission checks are done here. That's on the Account Controller.

        Args:
            new_email (str): The new email.

        Returns:
            normalized_email (str)
        """
        if not new_email:
            raise ValueError("Must set an email address!")
        new_email = AthanorAccount.objects.normalize_email(new_email)
        if AthanorAccount.objects.filter_family(email__iexact=new_email).exclude(id=self.id).count():
            raise ValueError("This email address is already in use!")
        self.email = new_email
        self.save(update_fields=['email'])
        return new_email

    def system_msg(self, text=None, system_name=None, enactor=None):
        sysmsg_border = self.options.sys_msg_border
        sysmsg_text = self.options.sys_msg_text
        formatted_text = f"|{sysmsg_border}-=<|n|{sysmsg_text}{system_name.upper()}|n|{sysmsg_border}>=-|n {text}"
        self.msg(text=formatted_text, system_name=system_name, original_text=text)

    def receive_template_message(self, text, msgobj, target):
        self.system_msg(text=text, system_name=msgobj.system_name)

    def render_list_section(self, enactor, styling):
        """
        Called by AccountController's list_accounts method. Renders this account
        on the list.
        """
        return [
            styling.styled_separator(self.username),
            f"|wEmail|n: {self.email}",
            f"|wLast Login|n: Last login here!",
            f"|wPermissions|n: {', '.join(self.permissions.all())} (Superuser: {self.is_superuser})",
            f"|wCharacters|n: {', '.join(str(c) for c in self.characters())}"
        ]

    def __str__(self):
        return self.key

    @classmethod
    def create_account(cls, *args, **kwargs):
        if not (email := kwargs.get('email', '')):
            raise ValueError("Must include an email!")
        if AthanorAccount.objects.filter_family(email__iexact=email).count():
            raise ValueError("Email is already in use by another account!")
        account, errors = cls.create(*args, **kwargs)
        if account:
            return account
        else:
            raise ValueError(errors)

    def rename(self, new_name):
        new_name = self.normalize_username(new_name)
        self.username = new_name
        self.save(update_fields=['username'])
        return new_name

    def generate_substitutions(self, viewer):
        return {
            "name": self.get_display_name(viewer),
            "email": self.email
        }

    def get_account(self):
        return self

    def characters(self):
        return self.player_character_components.filter(db_is_active=True)

    @lazy_property
    def styler(self):
        return athanor.api()['styler'](self)

    @lazy_property
    def colorizer(self):
        return self.get_or_create_attribute('colorizer', default=dict())

    def at_look(self, target=None, session=None, **kwargs):
        return self.return_appearance(looker=session)

    @lazy_property
    def appearance(self):
        return AccountAppearanceHandler(self)

    def return_appearance(self, looker, **kwargs):
        return self.appearance.render(looker, **kwargs)

    def check_lock(self, lock):
        return self.locks.check_lockstring(self, f"dummy:{lock}")

    def get_account(self):
        return self
