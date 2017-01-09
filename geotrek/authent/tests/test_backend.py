from django.test import TransactionTestCase

from django.db import connections
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from .base import AuthentFixturesMixin
from ..models import Structure
from ..backend import DatabaseBackend


_CREATE_TABLE_STATEMENT = """
    CREATE TABLE %s (
        username character varying(128) default '',
        first_name character varying(128) default '',
        last_name character varying(128) default '',
        password character varying(128) default '',
        email character varying(128) default '',
        level integer default 1,
        structure character varying(128) default '',
        lang character varying(2) default ''
    )"""


def query_db(sqlquery):
    connection = connections[settings.AUTHENT_DATABASE or 'default']
    cursor = connection.cursor()
    cursor.execute(sqlquery)
    return cursor


def password2md5(password):
    import hashlib
    return hashlib.md5(password).hexdigest()


@override_settings(AUTHENT_DATABASE='default',
                   AUTHENT_TABLENAME='authent_table',
                   AUTHENTICATION_BACKENDS=('geotrek.authent.backend.DatabaseBackend',))
class AuthentDatabaseTest(AuthentFixturesMixin, TransactionTestCase):
    def setUp(self):
        self.backend = DatabaseBackend()
        query_db(_CREATE_TABLE_STATEMENT % settings.AUTHENT_TABLENAME)
        self.deleted = False

    def tearDown(self):
        if not self.deleted:
            query_db("DROP TABLE IF EXISTS %s" % settings.AUTHENT_TABLENAME)

    @override_settings(AUTHENT_DATABASE=None)
    def test_base_missing(self):
        self.assertRaises(ImproperlyConfigured, self.backend.authenticate, ('toto', 'totopwd'))

    @override_settings(AUTHENT_TABLENAME=None)
    def test_table_missing(self):
        self.assertRaises(ImproperlyConfigured, self.backend.authenticate, ('toto', 'totopwd'))

    def test_raises_improperly_configured_when_tablemissing(self):
        query_db("DROP TABLE IF EXISTS %s" % settings.AUTHENT_TABLENAME)
        self.assertRaises(ImproperlyConfigured, self.backend.authenticate, ('toto', 'totopwd'))
        self.deleted = True

    def test_returns_none_if_user_is_invalid(self):
        self.assertEqual(None, self.backend.authenticate('toto', 'totopwd'))

    def test_invalid(self):
        self.assertEqual(None, self.backend.authenticate('toto', 'totopwd'))
        query_db("INSERT INTO %s (username, password) VALUES ('toto', '%s')" % (settings.AUTHENT_TABLENAME, password2md5('totopwd')))
        # Valid returns a user
        self.assertNotEqual(None, self.backend.authenticate('toto', 'totopwd'))
        # SQL injection safe ?
        self.assertEqual(None, self.backend.authenticate('toto', "' OR '' = '"))

    def test_login(self):
        query_db("INSERT INTO %s (username, password) VALUES ('harold', '%s')" % (settings.AUTHENT_TABLENAME, password2md5('kumar')))
        success = self.client.login(username="harold", password="kumar")
        self.assertTrue(success)
        response = self.client.get(reverse('core:path_list'))
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        query_db("INSERT INTO %s (username, password) VALUES ('marc', '%s')" % (settings.AUTHENT_TABLENAME, password2md5('maronnier')))
        success = self.client.login(username="marc", password="maronnier")
        self.assertTrue(success)
        self.client.logout()
        query_db("UPDATE %s SET password = '%s' WHERE username = 'marc'" % (settings.AUTHENT_TABLENAME, password2md5('maronier')))
        success = self.client.login(username="marc", password="maronnier")
        self.assertFalse(success)
        success = self.client.login(username="marc", password="maronier")
        self.assertTrue(success)

    def test_userprofile(self):
        query_db("INSERT INTO %s (username, password, first_name, last_name, structure, lang) VALUES ('aladeen', '%s', 'Ala', 'Deen', 'Walydia', 'ar')" % (settings.AUTHENT_TABLENAME, password2md5('aladeen')))
        user = self.backend.authenticate('aladeen', 'aladeen')
        self.assertEqual(user.first_name, 'Ala')
        self.assertEqual(user.last_name, 'Deen')
        self.assertEqual(user.profile.structure, Structure.objects.get(name='Walydia'))
        self.assertEqual(user.profile.language, 'ar')

    def test_usergroups(self):
        query_db("INSERT INTO %s (username, password) VALUES ('a', '%s')" % (settings.AUTHENT_TABLENAME, password2md5('a')))
        user = self.backend.authenticate('a', 'a')
        self.assertFalse(user.is_superuser)

        def test_level(username, level, groups):
            query_db("UPDATE %s SET level = %s WHERE username = '%s'" % (settings.AUTHENT_TABLENAME, level, username))
            user = self.backend.authenticate('a', 'a')
            if user:
                usergroups = user.groups.all()
                for group in groups:
                    self.assertTrue(Group.objects.get(id=group) in usergroups)
            return user

        user = test_level('a', 0, [])
        self.assertEqual(user, None)
        test_level('a', 2, [settings.AUTHENT_GROUPS_MAPPING['EDITOR']])
        test_level('a', 3, [settings.AUTHENT_GROUPS_MAPPING['PATH_MANAGER']])
        test_level('a', 4, [settings.AUTHENT_GROUPS_MAPPING['TREKKING_MANAGER']])
        user = test_level('a', 6, [])
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_get_user_returns_none_if_unknown(self):
        self.assertEqual(self.backend.get_user(-1), None)
