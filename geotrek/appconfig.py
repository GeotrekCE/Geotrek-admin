from __future__ import unicode_literals

from django.apps import AppConfig
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


class AuthConfig(GeotrekConfig):
    """
    bind for django.contrib.auth
    """
    name = 'django.contrib.auth'


class ContenttypeConfig(GeotrekConfig):
    """
    bind for django.contrib.contenttype
    """
    name = 'django.contrib.contenttypes'


class SessionConfig(GeotrekConfig):
    """
    bind for django.contrib.sessions
    """
    name = 'django.contrib.sessions'


class AdminConfig(GeotrekConfig):
    """
    bind for django.contrib.admin
    """
    name = 'django.contrib.admin'
