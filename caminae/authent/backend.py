import logging
from collections import namedtuple

from django.conf import settings
from django.contrib.auth.models import User, Group, check_password
from django.db import connections
from django.core.exceptions import ImproperlyConfigured

from .models import Structure, GROUP_PATH_MANAGER, GROUP_TREKKING_MANAGER, GROUP_EDITOR


logger = logging.getLogger(__name__)

FIELDS = 'username, first_name, last_name, password, email, level, structure, lang'.split(', ')

Credentials = namedtuple('Credentials', FIELDS)


class DatabaseBackend(object):
    """
    Authenticate against a table in Authent database.
    """
    def authenticate(self, username=None, password=None):
        credentials = self.query_credentials(username)
        if credentials and check_password(password, credentials.password):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(username, credentials.email, 'password_never_used')

            if credentials.level == 0:
                user.is_active = False
                user.save()
                return None  # no right

            self._update_infos(user, credentials)
            self._update_groups(user, credentials)

            return user
        return None

    def _update_infos(self, user, credentials):
        # Update infos
        user.is_active = True
        user.first_name = credentials.first_name
        user.last_name = credentials.last_name
        if credentials.level >= 3:
            user.is_staff = True   # can access adminsite
        if credentials.level >= 6:
            user.is_superuser = True   # all permissions
        user.save()

        # Update structure and lang
        profile = user.profile
        profile.structure, created = Structure.objects.get_or_create(name=credentials.structure)
        profile.language = credentials.lang
        profile.save()

    def _update_groups(self, user, credentials):
        # Set groups according to level
        editor_group, created = Group.objects.get_or_create(name=GROUP_EDITOR)
        path_manager_group, created = Group.objects.get_or_create(name=GROUP_PATH_MANAGER)
        trek_manager_group, created = Group.objects.get_or_create(name=GROUP_TREKKING_MANAGER)

        if credentials.level == 1:
            pass  # read-only
        user.groups.remove(editor_group)
        if credentials.level == 2:
            user.groups.add(editor_group)   # Editor
        user.groups.remove(path_manager_group)
        if credentials.level == 3:
            user.groups.add(path_manager_group)   # Path manager
        user.groups.remove(trek_manager_group)
        if credentials.level == 4:
            user.groups.add(trek_manager_group)   # Trekking manager

    def query_credentials(self, username):
        if not settings.AUTHENT_DATABASE:
            raise ImproperlyConfigured("Database backend is used, without AUTHENT_DATABASE setting.")
        if not settings.AUTHENT_TABLENAME:
            raise ImproperlyConfigured("Database backend is used, without AUTHENT_TABLENAME setting.")
        try:
            result = None
            cursor = connections[settings.AUTHENT_DATABASE].cursor()

            table_list = connections[settings.AUTHENT_DATABASE].introspection.get_table_list(cursor)
            tablename = settings.AUTHENT_TABLENAME if '.' not in settings.AUTHENT_TABLENAME else settings.AUTHENT_TABLENAME.split('.', 1)[1]
            if tablename not in table_list:
                raise ImproperlyConfigured("Database backend is used, and AUTHENT_TABLENAME does not exists.")

            sqlquery = "SELECT %s FROM %s WHERE username = " % (', '.join(FIELDS), settings.AUTHENT_TABLENAME)
            cursor.execute(sqlquery + "%s", [username])
            result = cursor.fetchone()
        except ImproperlyConfigured as e:
            connections[settings.AUTHENT_DATABASE].close()
            logger.exception(e)
            raise
        except Exception as e:
            connections[settings.AUTHENT_DATABASE].close()
            if settings.DEBUG or not settings.TEST:
                logger.exception(e)
        if result:
            return Credentials(*result)
        return None

    def get_user(self, user_id):
        try:
            u = User.objects.get(pk=user_id)
            return u
        except User.DoesNotExist:
            return None
