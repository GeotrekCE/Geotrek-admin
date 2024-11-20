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
from geotrek.cirkwi.tests.factories import CirkwiLocomotionFactory
from geotrek.common.models import FileType
from geotrek.common.utils import testdata
from geotrek.tourism.models import TouristicContent
from geotrek.trekking.models import Trek
from geotrek.trekking.tests.factories import (DifficultyLevelFactory,
                                              PracticeFactory)


class TestCirkwiTrekParserFr(CirkwiTrekParser):
    url = 'https://example.net/'
    create = True
    default_language = 'fr'


class TestCirkwiTrekParserFrNoCreate(CirkwiTrekParser):
    url = 'https://example.net/'
    create = False
    default_language = 'fr'


class TestCirkwiTrekParserFrUpdateOnly(CirkwiTrekParser):
    # Also tests using filename instead of url
    filename = "geotrek/cirkwi/tests/data/circuits_updated.xml"
    create = False
    update_only = True
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
        cls.locomotion = CirkwiLocomotionFactory(eid=2, name="Marche")
        cls.practice = PracticeFactory(name="Pédestre", cirkwi=cls.locomotion)
        PracticeFactory.create(name_fr="Vélo", name="Vélo")
        cls.difficulty = DifficultyLevelFactory(cirkwi_level=5)

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
        output = io.StringIO()
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTrekParserFr', verbosity=2, stdout=output)
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTrekParserEn', verbosity=0)
        self.assertEqual(Trek.objects.count(), 2)
        t = Trek.objects.get(name_fr="Le patrimoine de Plancoët")
        self.assertEqual(t.eid, '10925')
        self.assertEqual(t.name_en, "Title en")
        self.assertEqual(t.practice, self.practice)
        self.assertEqual(t.description_teaser_fr, 'Laissez-vous guider par ce chemin')
        self.assertEqual(t.description_teaser_en, "Description en")
        self.assertIn("Horaires: Tous les jours sauf le Dimanche", t.description_fr)
        self.assertIn("Au départ du terminal des car-ferrys.", t.description_fr)
        self.assertIn("Virer à droite, direction la plage-corniche de la Côte d'Opale.", t.description_fr)
        self.assertAlmostEqual(t.geom[0][0], 977776.9692000002)
        self.assertAlmostEqual(t.geom[0][1], 6547354.842799998)
        attachement = t.attachments.last()
        self.assertEqual(attachement.title, '')
        self.assertEqual(attachement.legend, 'Le patrimoine de Plancoët')
        self.assertEqual(attachement.author, 'Manon')
        self.assertEqual(attachement.attachment_file.size, len(testdata.IMG_FILE))
        self.assertEqual(t.duration, 2.0)
        t = Trek.objects.get(name_fr="Le patrimoine de Plancoët à vélo")
        self.assertEqual(t.eid, '10926')
        self.assertEqual(t.practice.name, "Vélo")
        # Assert created Ciwki Locomotion and mapped it to Practice
        self.assertEqual(t.practice.cirkwi.name, "Vélo")
        self.assertEqual(t.practice.cirkwi.eid, 3)
        self.assertEqual(t.description_teaser_fr, 'Laissez-vous guider par ce chemin')
        self.assertIn("Cirkwi Locomotion 'Vélo' n'existait pas dans Geotrek-Admin. Il a été créé automatiquement,", output.getvalue())
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTrekParserFrUpdateOnly', verbosity=2)
        self.assertEqual(Trek.objects.count(), 2)
        t = Trek.objects.get(name_fr="Le patrimoine de Plancoët à VTT")
        self.assertEqual(t.eid, '10926')
        self.assertEqual(t.description_teaser_fr, 'Laissez-vous guider par cette route')
        t = Trek.objects.get(name_fr="Le patrimoine de Plancoët")
        self.assertFalse(t.deleted)

    @mock.patch('requests.get')
    def test_create_touristic_content_no_type(self, mocked_get):
        output = io.StringIO()
        mocked_get.side_effect = self.make_dummy_get('poi.xml')
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTouristicContentDoNotCreateParserEn', verbosity=2, stdout=output)
        self.assertIn("Type 1 'Eglise' does not exist for category 'Monuments et Architecture'. Please add it",
                      output.getvalue())

    @mock.patch('requests.get')
    def test_create_trek_with_missing_locomotion(self, mocked_get):
        output = io.StringIO()
        mocked_get.side_effect = self.make_dummy_get('circuits_wrong_locomotion.xml')
        # Test Locomotion does not exist
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTrekParserFrNoCreate', verbosity=2, stdout=output)
        self.assertIn("Cirkwi Locomotion '['Aviron', '8']' n'existe pas dans Geotrek-Admin. Merci de l'ajouter,",
                      output.getvalue())
        # Test Locomotion exists but no related Practice is found
        CirkwiLocomotionFactory(name="Aviron", eid=8)
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTrekParserFrNoCreate', verbosity=2,
                     stdout=output)
        self.assertIn("Aucune Pratique ne correspond à la Locomotion Cirkwi 'Aviron' (id: '8'). Merci de l'ajouter,",
                      output.getvalue())

    @mock.patch('requests.get')
    def test_create_touristic_content(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('poi.xml')
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTouristicContentParserFr', verbosity=0)
        call_command('import', 'geotrek.cirkwi.tests.test_parsers.TestCirkwiTouristicContentParserEn', verbosity=0)
        self.assertEqual(TouristicContent.objects.count(), 2)
        tc = TouristicContent.objects.get(name_fr="Tour de lancienne église Sainte-Gertrude")
        self.assertEqual(tc.name_en, "Titre en anglais")
        self.assertEqual(tc.description_fr, 'A Tenneville, ce site reposant vous fera découvrir')
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
