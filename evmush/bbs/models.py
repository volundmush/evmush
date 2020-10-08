from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from evennia.typeclasses.models import TypedObject
from athanor.utils.time import utcnow


class BBSCategoryDB(TypedObject):
    __settingsclasspath__ = settings.BASE_BBS_CATEGORY_TYPECLASS
    __defaultclasspath__ = "athanor_bbs.bbs_categories.bbs_categories.DefaultBBSCategory"
    __applabel__ = "athanor_bbs"

    db_ikey = models.CharField(max_length=255, blank=False, null=False, unique=True)
    db_ckey = models.CharField(max_length=255, blank=False, null=False)
    db_abbr = models.CharField(max_length=5, blank=True, null=False)
    db_iabbr = models.CharField(max_length=5, unique=True, blank=True, null=False)
    db_cabbr = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        verbose_name = 'BBSCategory'
        verbose_name_plural = 'BBSCategories'

    def __str__(self):
        return str(self.db_key)


class BBSBoardDB(TypedObject):
    __settingsclasspath__ = settings.BASE_BBS_BOARD_TYPECLASS
    __defaultclasspath__ = "athanor_bbs.bbs_boards.bbs_boards.DefaultBBSBoard"
    __applabel__ = "athanor_bbs"

    db_category = models.ForeignKey(BBSCategoryDB, related_name='boards', null=False, on_delete=models.PROTECT)
    db_ikey = models.CharField(max_length=255, blank=False, null=False)
    db_ckey = models.CharField(max_length=255, blank=False, null=False)
    db_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.db_key)

    class Meta:
        verbose_name = 'BBS'
        verbose_name_plural = 'BBSs'
        unique_together = (('db_category', 'db_order'), ('db_category', 'db_ikey'))


class BBSPostDB(TypedObject):
    __settingsclasspath__ = settings.BASE_BBS_POST_TYPECLASS
    __defaultclasspath__ = "athanor_bbs.bbs_posts.bbs_posts.DefaultBBSPost"
    __applabel__ = "athanor_bbs"

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True)
    object_id = models.PositiveIntegerField(null=True)
    db_poster = GenericForeignKey('content_type', 'object_id')
    db_ckey = models.CharField(max_length=255, blank=False, null=False)
    db_date_created = models.DateTimeField(null=False)
    db_board = models.ForeignKey(BBSBoardDB, related_name='posts', on_delete=models.CASCADE)
    db_date_modified = models.DateTimeField(null=False)
    db_order = models.PositiveIntegerField(null=False)
    db_body = models.TextField(null=False, blank=False)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        unique_together = (('db_board', 'db_order'), )

    @classmethod
    def validate_key(cls, key_text, rename_from=None):
        return key_text

    @classmethod
    def validate_order(cls, order_text, rename_from=None):
        return int(order_text)

    def __str__(self):
        return self.subject

    def post_alias(self):
        return f"{self.board.alias}/{self.order}"

    def can_edit(self, checker=None):
        if self.owner.account_stub.account == checker:
            return True
        return self.board.check_permission(checker=checker, type="admin")

    def edit_post(self, find=None, replace=None):
        if not find:
            raise ValueError("No text entered to find.")
        if not replace:
            replace = ''
        self.date_modified = utcnow()
        self.text = self.text.replace(find, replace)

    def update_read(self, account):
        acc_read, created = self.read.get_or_create(account=account)
        acc_read.date_read = utcnow()
        acc_read.save()

    def fullname(self):
        return f"BBS Post: ({self.board.db_script.prefix_order}/{self.order}): {self.name}"

    def generate_substitutions(self, viewer):
        return {'name': self.name,
                'cname': self.cname,
                'typename': 'BBS Post',
                'fullname': self.fullname}


class BBSPostRead(models.Model):
    account = models.ForeignKey('accounts.AccountDB', related_name='bbs_read', on_delete=models.CASCADE)
    post = models.ForeignKey(BBSPostDB, related_name='read', on_delete=models.CASCADE)
    date_read = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('account', 'post'),)
