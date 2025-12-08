from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from ..backend import DatabaseBackend
from ..models import Structure
from .base import AuthentFixturesMixin

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
    connection = connections[settings.AUTHENT_DATABASE or "default"]
    with connection.cursor() as cursor:
        cursor.execute(sqlquery)


@override_settings(
    AUTHENT_DATABASE="default",
    AUTHENT_TABLENAME="authent_table",
    AUTHENTICATION_BACKENDS=("geotrek.authent.backend.DatabaseBackend",),
)
class AuthentDatabaseTest(AuthentFixturesMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.backend = DatabaseBackend()
        query_db(_CREATE_TABLE_STATEMENT % settings.AUTHENT_TABLENAME)
        cls.deleted = False

    def tearDown(self):
        if not self.deleted:
            query_db(f"DROP TABLE IF EXISTS {settings.AUTHENT_TABLENAME}")

    @override_settings(AUTHENT_DATABASE=None)
    def test_base_missing(self):
        self.assertRaises(
            ImproperlyConfigured, self.backend.authenticate, ("toto", "totopwd")
        )

    @override_settings(AUTHENT_TABLENAME=None)
    def test_table_missing(self):
        self.assertRaises(
            ImproperlyConfigured, self.backend.authenticate, ("toto", "totopwd")
        )

    def test_raises_improperly_configured_when_tablemissing(self):
        query_db(f"DROP TABLE IF EXISTS {settings.AUTHENT_TABLENAME}")
        self.assertRaises(
            ImproperlyConfigured, self.backend.authenticate, ("toto", "totopwd")
        )
        self.deleted = True

    def test_returns_none_if_user_is_invalid(self):
        self.assertEqual(
            None, self.backend.authenticate(username="toto", password="totopwd")
        )

    def test_invalid(self):
        self.assertEqual(
            None, self.backend.authenticate(username="toto", password="totopwd")
        )
        query_db(
            "INSERT INTO {} (username, password) VALUES ('toto', '{}')".format(
                settings.AUTHENT_TABLENAME, make_password("totopwd")
            )
        )
        # Valid returns a user
        self.assertNotEqual(
            None, self.backend.authenticate(username="toto", password="totopwd")
        )
        # SQL injection safe ?
        self.assertEqual(
            None, self.backend.authenticate(username="toto", password="' OR '' = '")
        )

    def test_login(self):
        query_db(
            "INSERT INTO {} (username, password) VALUES ('harold', '{}')".format(
                settings.AUTHENT_TABLENAME, make_password("kumar")
            )
        )
        success = self.client.login(username="harold", password="kumar")
        self.assertTrue(success)
        response = self.client.get(reverse("core:path_list"))
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        query_db(
            "INSERT INTO {} (username, password) VALUES ('marc', '{}')".format(
                settings.AUTHENT_TABLENAME, make_password("maronnier")
            )
        )
        success = self.client.login(username="marc", password="maronnier")
        self.assertTrue(success)
        self.client.logout()
        query_db(
            "UPDATE {} SET password = '{}' WHERE username = 'marc'".format(
                settings.AUTHENT_TABLENAME, make_password("maronier")
            )
        )
        success = self.client.login(username="marc", password="maronnier")
        self.assertFalse(success)
        success = self.client.login(username="marc", password="maronier")
        self.assertTrue(success)

    def test_userprofile(self):
        query_db(
            "INSERT INTO {} (username, password, first_name, last_name, structure, lang) VALUES ('aladeen', '{}', 'Ala', 'Deen', 'Walydia', 'ar')".format(
                settings.AUTHENT_TABLENAME, make_password("aladeen")
            )
        )
        user = self.backend.authenticate(username="aladeen", password="aladeen")
        self.assertEqual(user.first_name, "Ala")
        self.assertEqual(user.last_name, "Deen")
        self.assertEqual(user.profile.structure, Structure.objects.get(name="Walydia"))
        self.assertEqual(str(user.profile), "Profile for aladeen")

    def test_usergroups(self):
        query_db(
            "INSERT INTO {} (username, password) VALUES ('a', '{}')".format(
                settings.AUTHENT_TABLENAME, make_password("a")
            )
        )
        user = self.backend.authenticate(username="a", password="a")
        self.assertFalse(user.is_superuser)

        def test_level(username, level, groups):
            query_db(
                f"UPDATE {settings.AUTHENT_TABLENAME} SET level = {level} WHERE username = '{username}'"
            )
            user = self.backend.authenticate(username="a", password="a")
            if user:
                usergroups = user.groups.all()
                for group in groups:
                    self.assertTrue(Group.objects.get(id=group) in usergroups)
            return user

        user = test_level("a", 0, [])
        self.assertEqual(user, None)
        test_level("a", 2, [settings.AUTHENT_GROUPS_MAPPING["EDITOR"]])
        test_level("a", 3, [settings.AUTHENT_GROUPS_MAPPING["PATH_MANAGER"]])
        test_level("a", 4, [settings.AUTHENT_GROUPS_MAPPING["TREKKING_MANAGER"]])
        test_level(
            "a", 5, [settings.AUTHENT_GROUPS_MAPPING["EDITOR_TREKKING_MANAGEMENT"]]
        )
        user = test_level("a", 6, [])
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_get_user_returns_none_if_unknown(self):
        self.assertEqual(self.backend.get_user(-1), None)
