from athanor.utils.message import AdminMessage


class AccountMessage(AdminMessage):
    system_name = "ACCOUNT"
    targets = ['enactor', 'account', 'admin']


class CreateMessage(AccountMessage):
    messages = {
        'admin': "|w{enactor_name}|n created Account: |w{account_name}|n"
    }


class CreateMessageAdmin(CreateMessage):
    messages = {
        'enactor': "Successfully created Account: |w{account_name}|n with password: {password}",
        'admin': "|w{enactor_name}|n created Account: |w{account_name}|n with password: {password}"
    }


class RenameMessage(AccountMessage):
    messages = {
        'enactor': "Successfully renamed Account: |w{old_name}|n to |w{account_name}",
        'account': "|w{enactor_name}|n renamed your Account from |w{old_name}|n to |w{account_name}",
        'admin': "|w{enactor_name}|n renamed Account |w{old_name}|n to |w{account_name}"
    }


class EmailMessage(AccountMessage):
    messages = {
        'enactor': "Successfully changed Email for Account: |w{account_name}|n from |w{old_email}|n to |w{account_email}",
        'account': "|w{enactor_name}|n renamed your Account Email from |w{old_email}|n to |w{account_email}",
        'admin': "|w{enactor_name}|n changed Email for Account: |w{account_name}|n from |w{old_email}|n to |w{account_email}"
    }


class DisableMessage(AccountMessage):
    messages = {
        'enactor': "Successfully disabled Account: |w{account_name}|n under reasoning: {reason}",
        'account': "|w{enactor_name}|n disabled your Account due to: {reason}",
        'admin': "|w{enactor_name}|n disabled Account |w{account_name}|n under reasoning: {reason}"
    }


class EnableMessage(AccountMessage):
    messages = {
        'enactor': "Successfully re-enabled Account: |w{account_name}|n.",
        'account': "|w{enactor_name}|n re-enabled your Account.",
        'admin': "|w{enactor_name}|n re-enabled Account |w{account_name}|n."
    }


class BanMessage(AccountMessage):
    messages = {
        'enactor': "Successfully banned Account: |w{account_name}|n for {duration} - until {ban_date} - under reasoning: {reason}",
        'account': "|w{enactor_name}|n banned your Account for {duration} - until {ban_date} - due to: {reason}",
        'admin': "|w{enactor_name}|n banned Account |w{account_name}|n for {duration} - until {ban_date} - under reasoning: {reason}"
    }


class UnBanMessage(AccountMessage):
    messages = {
        'enactor': "Successfully un-banned Account: |w{account_name}|n.",
        'account': "|w{enactor_name}|n un-banned your Account.",
        'admin': "|w{enactor_name}|n un-banned Account |w{account_name}|n."
    }


class PasswordMessagePrivate(AccountMessage):
    messages = {
        'enactor': "Successfully changed your password!",
        'admin': "|w{enactor_name}|n changed their password!"
    }


class PasswordMessageAdmin(AccountMessage):
    messages = {
        'enactor': "Successfully changed the password for Account: |w{account_name}|n to |w{account_name}",
        'account': "|w{enactor_name}|n changed your Account's password!",
        'admin': "|w{enactor_name}|n changed Account |w{account_name}|n's password to |w{new_password}"
    }


class GrantMessage(AccountMessage):
    messages = {
        'enactor': "Successfully granted Account: |w{account_name}|n the Permission: |w{perm}|n",
        'account': "|w{enactor_name}|n granted your Account the Permission: |w{perm}|n",
        'admin': "|w{enactor_name}|n granted Account |w{account_name}|n the Permission: |w{perm}|n"
    }


class RevokeMessage(AccountMessage):
    messages = {
        'enactor': "Successfully revoked Account: |w{account_name}|n's use of the Permission: |w{perm}|n",
        'account': "|w{enactor_name}|n revoked Account's use of the Permission: |w{perm}|n",
        'admin': "|w{enactor_name}|n revoked Account |w{account_name}|n's use of the Permission: |w{perm}|n"
    }


class GrantSuperMessage(AccountMessage):
    messages = {
        'enactor': "Successfully granted Account: |w{account_name}|n the Permission: |rSUPERUSER|n",
        'account': "|w{enactor_name}|n granted your Account the Permission: |rSUPERUSER|n",
        'admin': "|w{enactor_name}|n granted Account |w{account_name}|n the Permission: |rSUPERUSER|n"
    }


class RevokeSuperMessage(AccountMessage):
    messages = {
        'enactor': "Successfully revoked Account: |w{account_name}|n's use of the Permission: |rSUPERUSER|n",
        'account': "|w{enactor_name}|n revoked Account's use of the Permission: |rSUPERUSER|n",
        'admin': "|w{enactor_name}|n revoked Account |w{account_name}|n's use of the Permission: |rSUPERUSER|n"
    }


class ForceDisconnect(AccountMessage):
    messages = {
        'enactor': "Successfully booted Account: |w{account_name}|n under reasoning: {reason}",
        'account': "|w{enactor_name}|n booted you for the reasoning: {reason}",
        'admin': "|w{enactor_name}|n booted Account: |w{account_name}|n under reasoning: {reason}"
    }
