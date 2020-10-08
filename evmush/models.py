from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from evennia.typeclasses.models import SharedMemoryModel, TypedObject


class HostAddress(models.Model):
    host_ip = models.GenericIPAddressField(null=False)
    host_name = models.TextField(null=True)

    def __str__(self):
        return str(self.host_ip)


class ProtocolName(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)

    def __str__(self):
        return str(self.name)


class Actor(SharedMemoryModel):
    db_account = models.ForeignKey('accounts.AccountDB', related_name='actors', on_delete=models.PROTECT)
    db_character = models.ForeignKey('objects.ObjectDB', related_name='actors', on_delete=models.PROTECT)


class MushObject(SharedMemoryModel):
    db_category = models.CharField(max_length=30, null=False)
    db_objid = models.CharField(max_length=255, null=False)
    db_timestamp_created = models.IntegerField(null=False)
    db_timestamp_modified = models.IntegerField(null=False)
    db_parent = models.ForeignKey('self', null=True, related_name='children', on_delete=models.SET_NULL)
    db_zone = models.ForeignKey('self', null=True, related_name='zoned', on_delete=models.SET_NULL)
    db_owner = models.ForeignKey('self', null=True, related_name='belongings', on_delete=models.SET_NULL)
    db_quota = models.IntegerField(default=0)
    db_cpu = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    db_abbr_category = models.PositiveSmallIntegerField(default=0)
    db_abbr = models.CharField(max_length=10, null=True, blank=False)
    inner = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('db_category', 'db_objid'), ('content_type', 'object_id'), ('db_abbr_category', 'db_abbr'))


class BaseProperty(models.Model):
    db_name = models.CharField(max_length=30, unique=True)
    db_system = models.BooleanField(default=False)
    db_internal = models.BooleanField(default=False)

    class Meta:
        abstract = True


class HasPerms(models.Model):
    db_see_perms = models.CharField(max_length=255, null=False, default="#TRUE")
    db_set_perms = models.CharField(max_length=255, null=False, default="#TRUE")
    db_reset_perms = models.CharField(max_length=255, null=False, default="#TRUE")

    class Meta:
        abstract = True


class Restriction(SharedMemoryModel, BaseProperty, HasPerms):
    db_command = models.BooleanField(default=False)
    db_function = models.BooleanField(default=False)


class AttrFlag(SharedMemoryModel, BaseProperty, HasPerms):
    db_letter = models.CharField(max_length=1, null=True, unique=True)


class FlagPerm(SharedMemoryModel, BaseProperty, HasPerms):
    pass


class LockFlag(SharedMemoryModel, BaseProperty, HasPerms):
    db_letter = models.CharField(max_length=1, null=True, unique=True)


class FuncFlag(SharedMemoryModel):
    pass


class CmdFlag(SharedMemoryModel, BaseProperty):
    pass


class MushCmd(SharedMemoryModel, BaseProperty):
    db_lock = models.CharField(max_length=255, null=False, default="#TRUE")
    db_flags = models.ManyToManyField('evmush.CmdFlag', related_name='cmds')
    db_restricts = models.ManyToManyField('evmush.Restriction', related_name='cmds')
    db_path = models.CharField(max_length=255, null=True)
    # Hooks are not stored in the database... they must be created via softcode and usually run at startup


class MushFnc(SharedMemoryModel, BaseProperty):
    db_flags = models.ManyToManyField('evmush.FuncFlag', related_name='functions')
    db_restrict = models.ManyToManyField('evmush.Restriction', related_name='functions')
    db_path = models.CharField(max_length=255, null=True)


class LockType(SharedMemoryModel):
    pass


class ObjFlag(SharedMemoryModel, BaseProperty, HasPerms):
    pass


class Attribute(SharedMemoryModel, BaseProperty):
    db_attrflags = models.ManyToManyField('evmush.AttrFlag', related_name='attributes')
    db_data = models.TextField(null=True)
    db_creator = models.ForeignKey('evmush.MushObject', null=True, related_name='created_attributes', on_delete=models.SET_NULL)


class PropAlias(SharedMemoryModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    db_alias = models.CharField(max_length=30)

    class Meta:
        unique_together = (('content_type', 'object_id', 'db_alias'),)


class ObjLock(SharedMemoryModel):
    db_mushobj = models.ForeignKey('evmush.MushObject', related_name='locks', on_delete=models.CASCADE)
    db_locktype = models.ForeignKey('evmush.LockType', related_name='holders', on_delete=models.PROTECT)
    db_value = models.TextField(blank=False, null=False, default='#FALSE')
    db_creator = models.ForeignKey('evmush.MushObject', null=True, related_name='created_locks', on_delete=models.SET_NULL)
    db_flags = models.ManyToManyField('evmush.LockFlag', related_name='obj_users')

    class Meta:
        unique_together = (('db_mushobj', 'db_locktype'),)


class ObjAttr(SharedMemoryModel):
    db_mushobj = models.ForeignKey('evmush.MushObject', related_name='attributes', on_delete=models.CASCADE)
    db_attr = models.ForeignKey('evmush.Attribute', related_name='holders', on_delete=models.PROTECT)
    db_owner = models.ForeignKey('evmush.MushObject', null=True, related_name='owned_attributes', on_delete=models.SET_NULL)
    db_flags = models.ManyToManyField('evmush.AttrFlag', related_name='objattrs')
    db_value = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (('db_mushobj', 'db_attr'),)


class BoardDB(TypedObject):
    """
    Component for Entities which ARE a BBS  Board.
    Beware, the NameComponent is considered case-insensitively unique per board Owner.
    """
    db_category = models.ForeignKey('evmush.GameDB', related_name='boards', null=True, on_delete=models.PROTECT)
    db_order = models.PositiveIntegerField(default=0)
    db_next_post_number = models.PositiveIntegerField(default=0, null=False)
    ignoring = models.ManyToManyField('accounts.AccountDB', related_name='ignored_boards')

    class Meta:
        unique_together = (('db_category', 'db_order'), ('db_category', 'db_key'))


class BBSPost(SharedMemoryModel):
    db_poster = models.ForeignKey('evmush.Actor', null=True, related_name='+', on_delete=models.PROTECT)
    db_name = models.CharField(max_length=255, blank=False, null=False)
    db_came = models.CharField(max_length=255, blank=False, null=False)
    db_date_created = models.DateTimeField(null=False)
    db_board = models.ForeignKey('evmush.BoardDB', related_name='+', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(null=False)
    db_order = models.PositiveIntegerField(null=False)
    db_body = models.TextField(null=False, blank=False)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_board', 'db_order'), )


class BBSPostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(BBSPost, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'post'),)
