from django.contrib.contenttypes.fields import GenericRelation
from evmush.models import MushObject


class MushBase:
    meta_type = None
    meta_letter = None
    mbase = GenericRelation(MushObject, content_type_field='content_type', object_id_field='object_id')

    @property
    def mobj(self):
        self.mbase.first()
