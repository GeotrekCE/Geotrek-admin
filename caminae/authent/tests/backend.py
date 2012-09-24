from django.test import TestCase
from django.test.utils import override_settings

from caminae.authent.fixtures.development import populate_groups


@override_settings(AUTHENT_DATABASE='default')
class StructureTest(TestCase):
    def setUp(self):
        populate_groups() # TODO not best :/

    def test_tablemissing(self):
        pass  # TODO
    
    def test_missing(self):
        pass
    
    def test_update(self):
        pass
    
    def test_groups(self):
        pass

    def test_invalid(self):
        # wrong password
        # sql injection
