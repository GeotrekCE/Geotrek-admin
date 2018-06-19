import os

from django.core.management import call_command
from django.test import TestCase


class StructureParserTest(TestCase):
    def test_load_shp(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        call_command('loadsignage', filename, verbosity=0, type_default='Signage', name_default='name',
                     label_default='label', condition_default='condition', structure_default='structure',
                     description_default='description', year_default=0)
