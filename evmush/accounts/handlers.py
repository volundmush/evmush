"""
Contains only Handlers relevant to Accounts.
"""
import time
from django.utils import timezone
from django.conf import settings
from evennia import MONITOR_HANDLER
from athanor.utils.time import utcnow
from athanor.utils.link import EntitySessionHandler
from athanor.utils.cmdsethandler import AthanorCmdSetHandler
from athanor.utils.cmdhandler import CmdHandler
from athanor.utils.appearance import AppearanceHandler


class BanHandler:

    def __init__(self, account):
        self.account = account
        self.state = None
        self.load()

    def load(self):
        self.state = self.account.attributes.get(key='ban', category='system', default=dict())

    def get_state(self):
        """

        Returns:
            False if not banned. dict of stuff if yes.
        """
        if (banned_until := self.state.get('until', None)) and banned_until > (now := utcnow()):
            return {
                'left': banned_until - now,
                'reason': self.state.get('reason', 'none given'),
                'until': banned_until
            }
        if banned_until and banned_until < now:
            self.clear()
        return False

    def clear(self):
        self.account.attributes.remove(key='ban', category='system')
        self.load()

    def set(self, account, until, reason):
        new_ban = {
            'account': account,
            'until': until,
            'reason': reason,
            'started': utcnow()
        }
        self.account.attributes.add(key='ban', category='system', value=new_ban)
        self.load()


class AccountSessionHandler(EntitySessionHandler):

    def validate_link_request(self, session, force=False, sync=False, **kwargs):
        """
        Nothing really to do here. Accounts are validated through their password. That's .authenticate().
        """
        pass

    def at_before_link_session(self, session, force=False, sync=False, **kwargs):
        existing = self.all()
        if settings.MULTISESSION_MODE == 0:
            # disconnect all previous sessions.
            # session.connectionhandler.disconnect_duplicate_sessions(session)
            pass  # I will make this work later

    def at_link_session(self, session, force=False, sync=False, **kwargs):
        session.logged_in = True
        session.account = self.obj
        session.uname = self.obj.name
        session.uid = self.obj.pk
        session.conn_time = time.time()
        session.swap_cmdset(settings.CMDSET_SELECTSCREEN)

    def at_after_link_session(self, session, force=False, sync=False, **kwargs):
        self.obj.at_init()
        # Check if this is the first time the *account* logs in
        if self.obj.db.FIRST_LOGIN:
            self.obj.at_first_login()
            del self.obj.db.FIRST_LOGIN
        self.obj.last_login = timezone.now()
        self.obj.save()
        nsess = self.count()
        session.log(f"Logged in: {self} {session.address} ({nsess} session(s) total)")
        if nsess < 2:
            pass

        #    SIGNAL_ACCOUNT_POST_FIRST_LOGIN.send(sender=self, session=session)
        #  SIGNAL_ACCOUNT_POST_LOGIN.send(sender=self, session=session)

    def validate_unlink_request(self, session, force=False, reason=None, **kwargs):
        pass

    def at_before_unlink_session(self, session, force=False, reason=None, **kwargs):
        pass

    def at_unlink_session(self, session, force=False, reason=None, **kwargs):
        session.account = None
        session.logged_in = False
        session.uid = None
        session.uname = None
        session.cmdset.add(settings.CMDSET_LOGINSCREEN, permanent=True, default_cmdset=True)
        session.cmdset.update(init_mode=True)

    def at_after_unlink_session(self, session, force=False, reason=None, **kwargs):
        if not (remaining := self.all()):
            self.obj.attributes.add(key="last_active_datetime", category="system", value=timezone.now())
            self.obj.is_connected = False
        MONITOR_HANDLER.remove(self.obj, "_saved_webclient_options", session.sessid)

        session.log(f"Logged out: {self.obj} {session.address} ({len(remaining)} sessions(s) remaining)"
                    f"{reason if reason else ''}")

        if not remaining:
            pass
            # SIGNAL_ACCOUNT_POST_LAST_LOGOUT.send(sender=session.account, session=session)
        # SIGNAL_ACCOUNT_POST_LOGOUT.send(sender=session.account, session=session)
        sessid = session.sessid


class AccountCmdSetHandler(AthanorCmdSetHandler):

    def get_channel_cmdsets(self, caller, merged_current):
        return []

    def gather_extra(self, caller, merged_current):
        cmdsets = []
        if not merged_current.no_channels:
            cmdsets.extend(self.get_channel_cmdsets(caller, merged_current))
        return cmdsets


class AccountCmdHandler(CmdHandler):
    session = None

    def get_cmdobjects(self, session=None):
        cmdobjects = super().get_cmdobjects(session)
        cmdobjects['account'] = self.cmdobj
        if not (sess := cmdobjects.get('session', None)):
            return cmdobjects
        if (play_sess := sess.get_play_session()):
            cmdobjects['playsession'] = play_sess
            cmdobjects['avatar'] = play_sess.get_avatar()
            cmdobjects['player_character'] = play_sess.get_player_character()
        return cmdobjects


class AccountAppearanceHandler(AppearanceHandler):
    hooks = ['header', 'details', 'sessions', 'characters', 'commands']

    def details(self, looker, styling, **kwargs):
        return [
            styling.styled_header(f"Account: {self.obj.username}"),
            f"|wEmail:|n {self.obj.email}"
        ]

    def sessions(self, looker, styling, **kwargs):
        message = list()
        if (sessions := self.obj.sessions.all()):
            message.append(styling.styled_separator("Sessions"))
            for sess in sessions:
                message.append(sess.render_character_menu_line(looker))
        return message

    def characters(self, looker, styling, **kwargs):
        message = list()
        if (characters := self.obj.characters()):
            message.append(styling.styled_separator("Characters"))
            for char in characters:
                message.append(char.render_character_menu_line(looker))
        return message

    def commands(self, looker, styling, **kwargs):
        message = list()
        caller_admin = self.obj.check_lock("pperm(Admin)")
        message.append(styling.styled_separator(looker, "Commands"))
        if not settings.RESTRICTED_CHARACTER_CREATION or caller_admin:
            message.append("|w@charcreate <name>|n to create a Character.")
        if not settings.RESTRICTED_CHARACTER_DELETION or caller_admin:
            message.append("|w@chardelete <name>=<verify name>|n to delete a character.")
        if not settings.RESTRICTED_CHARACTER_RENAME or caller_admin:
            message.append("|w@charrename <character>=<new name>|n to rename a character.")
        if not settings.RESTRICTED_ACCOUNT_RENAME or caller_admin:
            message.append("|w@username <name>|n to change your Account username.")
        if not settings.RESTRICTED_ACCOUNT_EMAIL or caller_admin:
            message.append("|w@email <new email>|n to change your Email")
        if not settings.RESTRICTED_ACCOUNT_PASSWORD or caller_admin:
            message.append("|w@password <old>=<new>|n to change your password.")
        message.append("|w@ic <name>|n to enter the game as a Character.")
        message.append("|w@ooc|n to return here again.")
        message.append("|whelp|n for more information.")
        message.append("|wQUIT|n to disconnect.")
        return message
