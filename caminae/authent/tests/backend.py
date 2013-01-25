from django.db import connections, DatabaseError
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from caminae.authent.fixtures.development import populate_groups

from ..models import Structure, GROUP_PATH_MANAGER, GROUP_TREKKING_MANAGER, GROUP_EDITOR
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
    cursor = connections[settings.AUTHENT_DATABASE].cursor()
    cursor.execute(sqlquery)    
    return cursor

def password2md5(password):
    import hashlib
    return hashlib.md5(password).hexdigest()


@override_settings(AUTHENT_DATABASE='default', 
                   AUTHENT_TABLENAME='authent_table', 
                   AUTHENTICATION_BACKENDS=('caminae.authent.backend.DatabaseBackend',))
class AuthentDatabaseTest(TestCase):
    def setUp(self):
        populate_groups() # TODO not best :/
        self.backend = DatabaseBackend()
        query_db(_CREATE_TABLE_STATEMENT % settings.AUTHENT_TABLENAME)

    @override_settings(AUTHENT_TABLENAME=None)
    def test_confmissing(self):
        self.assertRaises(ImproperlyConfigured, self.backend.authenticate, ('toto', 'totopwd'))

    def test_conftablemissing(self):
        query_db("DROP TABLE IF EXISTS %s;" % settings.AUTHENT_TABLENAME)
        self.assertRaises(ImproperlyConfigured, self.backend.authenticate, ('toto', 'totopwd'))
        query_db(_CREATE_TABLE_STATEMENT %  settings.AUTHENT_TABLENAME)
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
            usergroups = user.groups.all()
            for group in groups:
                self.assertTrue(Group.objects.get(name=group) in usergroups)
            return user

        test_level('a', 2, [GROUP_EDITOR])
        test_level('a', 3, [GROUP_PATH_MANAGER])
        test_level('a', 4, [GROUP_TREKKING_MANAGER])
        user = test_level('a', 6, [])
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
