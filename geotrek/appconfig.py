from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.contrib.sessions.apps import SessionsConfig
from django.db.models.signals import post_migrate, pre_migrate

from geotrek.common.utils.signals import pm_callback, check_srid_has_meter_unit


class GeotrekConfig(AppConfig):
    """
    Base class to handle table move on right schemas, and load SQL files
    !! WARNING !! need to create subclass in geotrek.myapp.apps for project apps,
    and create subclasses here for external subclasses
    """
    def __init__(self, *args, **kwargs):
        pre_migrate.connect(check_srid_has_meter_unit, sender=self, dispatch_uid='geotrek.core.checksrid')
        super(GeotrekConfig, self).__init__(*args, **kwargs)

    def ready(self):
        post_migrate.connect(pm_callback, sender=self, dispatch_uid='geotrek.core.movetoschemas')


class AuthGeotrekConfig(AuthConfig, GeotrekConfig):
    """
    bind for django.contrib.auth
    """
    pass


class ContenttypeGeotrekConfig(ContentTypesConfig, GeotrekConfig):
    """
    bind for django.contrib.contenttype
    """
    pass


class SessionsGeotrekConfig(SessionsConfig, GeotrekConfig):
    pass


class AdminGeotrekConfig(AdminConfig, GeotrekConfig):
    pass


class CeleryGeotrekConfig(GeotrekConfig):
    name = 'djcelery'
    verbose_name = 'Django Celery'


class EasyThumbnailsGeotrekConfig(GeotrekConfig):
    name = 'easy_thumbnails'
    verbose_name = 'Easy thumbnails'
