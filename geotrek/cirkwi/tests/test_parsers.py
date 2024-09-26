import io
import os
from copy import copy
from unittest import mock, skipIf
from unittest.mock import Mock

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from geotrek.cirkwi.parsers import (CirkwiTouristicContentParser,
                                    CirkwiTrekParser)
from geotrek.common.models import FileType
from geotrek.common.utils import testdata
from geotrek.tourism.models import TouristicContent
from geotrek.trekking.models import Trek


class TestCirkwiTrekParserFr(CirkwiTrekParser):
    url = 'https://example.net/'
    default_language = 'fr'


class TestCirkwiTrekParserEn(CirkwiTrekParser):
    url = 'https://example.net/'
    default_language = 'en'
    # English parser must not delete attachments created by French parser
    delete_attachments = False


class TestCirkwiTouristicContentParserFr(CirkwiTouristicContentParser):
    url = 'https://example.net/'
    default_language = 'fr'


class TestCirkwiTouristicContentDoNotCreateParserEn(CirkwiTouristicContentParser):
    url = 'https://example.net/'
    default_language = 'en'
    # English parser must not delete attachments created by French parser
    delete_attachments = False
    field_options = {
        "geom": {"required": True},
        "name": {"required": True},
        'category': {'create': True},
    }


class TestCirkwiTouristicContentParserEn(CirkwiTouristicContentParser):
    url = 'https://example.net/'
    default_language = 'en'
    # English parser must not delete attachments created by French parser
    delete_attachments = False


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
class CirkwiParserTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    def make_dummy_get(self, data_filename):
        def dummy_get(url, *args, **kwargs):
            rv = Mock()
            rv.status_code = 200
            if ".jpg" in url:
                rv.content = copy(testdata.IMG_FILE)
            elif ".gpx" in url:
                filename = "geotrek/cirkwi/tests/data/trek.gpx"
                with open(filename, 'r') as f:
                    geodata = f.read()
                rv.content = bytes(geodata, 'utf-8')
            else:
                filename = os.path.join("geotrek/cirkwi/tests/data/", data_filename)
                with open(filename, 'r') as f:
                    rv.content = f.read()
            return rv

        return dummy_get

    @mock.patch('requests.get')
    def test_create_treks(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('circuits.xml')
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTrekParserFr', verbosity=0)
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTrekParserEn', verbosity=0)
        self.assertEqual(Trek.objects.count(), 1)
        t = Trek.objects.first()
        self.assertEqual(t.name_fr, "Le patrimoine de Plancoët")
        self.assertEqual(t.name_en, "Title en")
        self.assertEqual(t.description_fr, 'Laissez-vous guider par ce chemin\n\n\nHoraires: Tous les jours sauf le Dimanche')
        self.assertEqual(t.description_en, "Description en")
        self.assertAlmostEqual(t.geom[0][0], 977776.9692000002)
        self.assertAlmostEqual(t.geom[0][1], 6547354.842799998)
        attachement = t.attachments.last()
        self.assertEqual(attachement.title, '')
        self.assertEqual(attachement.legend, 'Le patrimoine de Plancoët')
        self.assertEqual(attachement.author, 'Manon')
        self.assertEqual(attachement.attachment_file.size, len(testdata.IMG_FILE))

    @mock.patch('requests.get')
    def test_create_touristic_content_no_type(self, mocked_get):
        output = io.StringIO()
        mocked_get.side_effect = self.make_dummy_get('poi.xml')
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTouristicContentDoNotCreateParserEn', verbosity=2, stdout=output)
        self.assertIn("Type 1 'Eglise' does not exist for category 'Monuments et Architecture'. Please add it",
                      output.getvalue())

    @mock.patch('requests.get')
    def test_create_touristic_content(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('poi.xml')
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTouristicContentParserFr', verbosity=0)
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTouristicContentParserEn', verbosity=0)
        self.assertEqual(TouristicContent.objects.count(), 1)
        tc = TouristicContent.objects.first()
        self.assertEqual(tc.name_fr, "Tour de lancienne église Sainte-Gertrude")
        self.assertEqual(tc.name_en, "Titre en anglais")
        self.assertEqual(tc.description_fr, 'A Tenneville, ce site reposant vous fera découvrir\n\n\nHoraire: Ouvert du Lundi au Vendredi de 8h à 19h')
        self.assertEqual(tc.description_en, "Description en anglais")
        self.assertEqual(tc.practical_info_fr, "<strong>Adresse : </strong><br>1 route de Bastogne<br>6970 Tenneville<br><br><strong>Horaire : </strong><br>Ouvert du Lundi au Vendredi de 8h à 19h<br><br><strong>Contact : </strong><br>Téléphone: 01 02 03 04 05<br>")
        self.assertEqual(str(tc.category), "Monuments et Architecture")
        self.assertEqual(str(tc.type1.first()), "Eglise")
        self.assertAlmostEqual(tc.geom.x, 931284.9680097454)
        self.assertAlmostEqual(tc.geom.y, 6850434.12975747)
        self.assertEqual(tc.attachments.count(), 2)
        attachement = tc.attachments.last()
        self.assertEqual(attachement.title, '')
        self.assertEqual(attachement.legend, 'Le patrimoine de Plancoët')
        self.assertEqual(attachement.author, 'Manon')
        self.assertEqual(attachement.attachment_file.size, len(testdata.IMG_FILE))
