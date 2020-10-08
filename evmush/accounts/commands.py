from evennia.contrib.unixcommand import UnixCommand

import athanor
from athanor.utils.command import AthanorCommand


class AdministrationCommand(AthanorCommand):
    help_category = "Account Management"
    controller_key = 'account'
    account_caller = True


class CmdAccount(AdministrationCommand):
    """
    General command for controlling game accounts.
    Note that <account> accepts either username or email address.

    Usage:
        @account [<account>]
            Display a breakdown of information all about an Account.
            Your own, if not targeted.

        @account/list
            Show all accounts in the system.

        @account/create <username>,<email>,<password>
            Create a new account.

        @account/disable <account>=<reason>
            Indefinitely disable an Account. The stated reason will be shown
            to staff and the account. If the account is currently online,
            it will be booted.
            Use @account/enable <account> to re-enable the account.

        @account/ban <account>=<duration>,<reason>
            Temporarily disable an account until the timer's up. <duration>
            must be a time period such as 7d (7 days), 2w (2 weeks), etc.
            Reason will be shown to the account and staff and recorded.
            Use @account/unban <account> to lift it early.

        @account/rename <account>=<new name>
            Change an account's Username.

        @account/email <account>=<new email>
            Change an Account's email address.

        @account/password <account>=<new password>
            Re-set an Account's password.

        @account/boot <account>=<reason>
            Forcibly disconnect an Account.
    """
    key = '@account'
    locks = "cmd:pperm(Helper)"
    switch_options = ('list', 'create', 'disable', 'enable', 'rename', 'ban', 'unban', 'password', 'email', 'boot')
    args_delim = ','
    switch_syntax = {
        'create': "<username>,<email>,<password>",
        'disable': '<account>=<reason>',
        'enable': '<account>',
        'main': '<account>',
        'rename': '<account>=<new name>',
        'ban': '<account>=<duration>,<reason>',
        'unban': '<account>',
        'email': '<account>=<new email>',
        'password': '<account>=<new password>',
        'boot': '<account>=<reason>',
        'main': '<account>'
    }

    def switch_main(self):
        if not self.args:
            self.args = self.account
        self.msg(self.controller.examine_account(self.session, self.args))

    def switch_list(self):
        self.msg(self.controller.list_accounts(self.session))

    def switch_create(self):
        if not len(self.argslist) == 3:
            self.syntax_error()
        username, email, password = self.argslist
        self.controller.create_account(self.session, username, email, password)

    def switch_disable(self):
        self.controller.disable_account(self.session, self.lhs, self.rhs)

    def switch_enable(self):
        self.controller.enable_account(self.session, self.lhs)

    def switch_password(self):
        self.controller.password_account(self.session, self.lhs, self.rhs)

    def switch_email(self):
        self.controller.email_account(self.session, self.lhs, self.rhs)

    def switch_boot(self):
        self.controller.disconnect_account(self.session, self.lhs, self.rhs)


class CmdAccess(AdministrationCommand):
    """
    Displays and manages information about Account access permissions.

    Usage:
        @access [<account>]
            Show the target's access details. Your own, if none is provided.

        @access/grant <account>=<permission>
            Grant an Evennia Permission to an Account.
            Use @access/revoke <account>=<permission> to remove it.

        @access/all
            Displays all grantable normal Permissions and their descriptions.

        @access/directory
            Display all managed Permissions and which Accounts hold them.
            Could be very spammy.

        @access/super <account>=SUPER DUPER
            Promote an Account to Superuser status. Use again to demote.
            Silly verification string required for accident prevention.
            |rDANGEROUS.|n
    """
    key = "@access"
    locks = "cmd:pperm(Helper)"
    switch_rules = {
        'directory': dict(),
        'super': {
            'syntax': "<account>=SUPER DUPER",
            'lhs_req': True,
            'rhs_req': True
        },
        'grant': {
            'syntax': "<account>=<permission>",
            'lhs_req': True,
            'rhs_req': True
        },
        'all': dict(),
        'revoke': {
            'syntax': '<account>=<permission>',
            'lhs_req': True,
            'rhs_req': True
        }
    }
    switch_options = ['directory', 'super', 'grant', 'all', 'revoke']

    def switch_main(self):
        account = self.args if self.args else self.account
        self.msg(self.controller.access_account(self.session, account))

    def switch_grant(self):
        self.controller.grant_permission(self.session, self.lhs, self.rhs)

    def switch_revoke(self):
        self.controller.revoke_permission(self.session, self.lhs, self.rhs)

    def switch_super(self):
        if self.rhs != "SUPER DUPER":
            raise ValueError("Usage: @account/super <account>=SUPER DUPER")
        self.controller.toggle_super(self.session, self.lhs)

    def switch_all(self):
        self.msg(self.controller.list_permissions(self.session))

    def switch_directory(self):
        self.msg(self.controller.permissions_directory(self.session))
