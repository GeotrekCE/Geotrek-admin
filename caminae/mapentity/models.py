import os
import time
from datetime import datetime
from urlparse import urljoin

from django.db import models
from django.conf import settings
from django.utils import timezone

from screamshot.utils import casperjs_capture


# Used to create the matching url name
ENTITY_LAYER = "layer"
ENTITY_LIST = "list"
ENTITY_JSON_LIST = "json_list"
ENTITY_FORMAT_LIST = "format_list"
ENTITY_DETAIL = "detail"
ENTITY_DOCUMENT = "document"
ENTITY_CREATE = "add"
ENTITY_UPDATE = "update"
ENTITY_DELETE = "delete"

ENTITY_KINDS = (
    ENTITY_LAYER, ENTITY_LIST, ENTITY_JSON_LIST,
    ENTITY_FORMAT_LIST, ENTITY_DETAIL, ENTITY_DOCUMENT, ENTITY_CREATE,
    ENTITY_UPDATE, ENTITY_DELETE,
)

class MapEntityMixin(object):

    @classmethod
    def latest_updated(cls):
        try:
            return cls.objects.latest("date_update").date_update
        except cls.DoesNotExist:
            return None

    # List all different kind of views
    @classmethod
    def get_url_name(cls, kind):
        if not kind in ENTITY_KINDS:
            return None
        return '%s:%s_%s' % (cls._meta.app_label, cls._meta.module_name, kind)

    @classmethod
    def get_url_name_for_registration(cls, kind):
        if not kind in ENTITY_KINDS:
            return None
        return '%s_%s' % (cls._meta.module_name, kind)

    @classmethod
    @models.permalink
    def get_layer_url(cls):
        return (cls.get_url_name(ENTITY_LAYER), )

    @classmethod
    @models.permalink
    def get_list_url(cls):
        return (cls.get_url_name(ENTITY_LIST), )

    @classmethod
    @models.permalink
    def get_jsonlist_url(cls):
        return (cls.get_url_name(ENTITY_JSON_LIST), )

    @classmethod
    @models.permalink
    def get_format_list_url(cls):
        return (cls.get_url_name(ENTITY_FORMAT_LIST), )

    @classmethod
    @models.permalink
    def get_add_url(cls):
        return (cls.get_url_name(ENTITY_CREATE), )

    def get_absolute_url(self):
        return self.get_detail_url()

    @classmethod
    @models.permalink
    def get_generic_detail_url(self):
        return (self.get_url_name(ENTITY_DETAIL), [str(0)])

    @models.permalink
    def get_detail_url(self):
        return (self.get_url_name(ENTITY_DETAIL), [str(self.pk)])

    def prepare_map_image(self, rooturl):
        path = self.get_map_image_path()
        # If already exists and up-to-date, do nothing
        if os.path.exists(path):
            modified = datetime.fromtimestamp(os.path.getmtime(path))
            modified = modified.replace(tzinfo=timezone.utc)
            if modified > self.date_update:
                return
        # Run head-less capture
        url = urljoin(rooturl, self.get_detail_url())
        with open(path, 'wb') as f:
            casperjs_capture(f, url, selector='.map-panel')
        # TODO : remove capture image file on delete

    def get_map_image_path(self):
        basefolder = os.path.join(settings.MEDIA_ROOT, 'maps')
        if not os.path.exists(basefolder):
            os.mkdir(basefolder)
        return os.path.join(basefolder, '%s-%s.png' % (self._meta.module_name, self.pk))

    def get_map_image_url(self):
        return os.path.join(settings.MEDIA_URL, 'maps', '%s-%s.png' % (self._meta.module_name, self.pk))

    @models.permalink
    def get_document_url(self):
        return (self.get_url_name(ENTITY_DOCUMENT), [str(self.pk)])

    @models.permalink
    def get_update_url(self):
        return (self.get_url_name(ENTITY_UPDATE), [str(self.pk)])

    @models.permalink
    def get_delete_url(self):
        return (self.get_url_name(ENTITY_DELETE), [str(self.pk)])
