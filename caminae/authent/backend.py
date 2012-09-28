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
            # Update infos
            user.first_name = credentials.first_name
            user.last_name = credentials.last_name
            user.save()
            profile = user.profile
            profile.structure, created = Structure.objects.get_or_create(name=credentials.structure)
            profile.language = credentials.lang
            profile.save()
            
            # Set groups according to level
            if credentials.level == 0:
                user.is_active = False
                return None  # no right
            user.is_active = True
            if credentials.level == 1:
                pass  # read-only
            if credentials.level == 2:
                editor_group, created = Group.objects.get_or_create(name=GROUP_EDITOR)
                user.groups.add(editor_group)   # Editor
            if credentials.level == 3:
                path_manager_group, created = Group.objects.get_or_create(name=GROUP_PATH_MANAGER)
                user.groups.add(path_manager_group)   # Path manager
            if credentials.level == 4:
                trek_manager_group, created = Group.objects.get_or_create(name=GROUP_TREKKING_MANAGER)
                user.groups.add(trek_manager_group)   # Trekking manager
            
            if credentials.level >= 3:
                user.is_staff = True   # can access adminsite
            if credentials.level >= 6:
                user.is_superuser = True   # all permissions
            return user
        return None

    def query_credentials(self, username):
        if not settings.AUTHENT_DATABASE:
            raise ImproperlyConfigured("Database backend is used, without AUTHENT_DATABASE setting.")
        if not settings.AUTHENT_TABLENAME:
            raise ImproperlyConfigured("Database backend is used, without AUTHENT_TABLENAME setting.")
        try:
            cursor = connections[settings.AUTHENT_DATABASE].cursor()
            sqlquery = "SELECT %s FROM %s WHERE username = " % (','.join(FIELDS), settings.AUTHENT_TABLENAME)
            cursor.execute(sqlquery + "%s", [username])
            result = cursor.fetchone()
        except Exception, e:
            logger.exception(e)
            connections[settings.AUTHENT_DATABASE].close()
            raise
        if result:
            return Credentials(*result)
        return None

    def get_user(self, user_id):
        try:
            u = User.objects.get(pk=user_id)
            return u
        except User.DoesNotExist:
            return None
