from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.contrib.sessions.apps import SessionsConfig
from django.db.models.signals import post_migrate
from django_celery_results.apps import CeleryResultConfig

from geotrek.common.utils.signals import check_srid_has_meter_unit, pm_callback


class GeotrekConfig(AppConfig):
    """
    Base class to handle table move on right schemas, and load SQL files
    !! WARNING !! need to create subclass in geotrek.myapp.apps for project apps,
    and create subclasses here for external subclasses
    """
    def ready(self):
        post_migrate.connect(pm_callback, sender=self, dispatch_uid='geotrek.core.pm_callback')
        check_srid_has_meter_unit()


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


class CeleryGeotrekConfig(GeotrekConfig, CeleryResultConfig):
    pass


class EasyThumbnailsGeotrekConfig(GeotrekConfig):
    name = 'easy_thumbnails'
    verbose_name = 'Easy thumbnails'
