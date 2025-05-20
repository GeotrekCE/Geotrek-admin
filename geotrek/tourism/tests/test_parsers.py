import io
import json
import os
from datetime import date
from unittest import mock

import requests
from django.contrib.gis.geos import LineString, Point, Polygon
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from geotrek.common.models import Attachment, FileType
from geotrek.common.tests.factories import RecordSourceFactory, TargetPortalFactory
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.tourism.models import InformationDesk, TouristicContent, TouristicEvent
from geotrek.tourism.parsers import (
    EspritParcParser,
    GeotrekInformationDeskParser,
    GeotrekTouristicContentParser,
    GeotrekTouristicEventParser,
    InformationDeskApidaeParser,
    InformationDeskOpenStreetMapParser,
    LEITouristicContentParser,
    LEITouristicEventParser,
    OpenStreetMapTouristicContentParser,
    TouristicContentApidaeParser,
    TouristicContentTourInSoftParser,
    TouristicContentTourInSoftParserV3,
    TouristicContentTourInSoftParserV3withMedias,
    TouristicEventApidaeParser,
    TouristicEventTourInSoftParser,
)
from geotrek.tourism.tests.factories import (
    InformationDeskTypeFactory,
    TouristicContentCategoryFactory,
    TouristicContentType1Factory,
    TouristicContentType2Factory,
    TouristicEventTypeFactory,
)


class ApidaeConstantFieldContentParser(TouristicContentApidaeParser):
    category = "Constant Content"
    type1 = ["Type1 1", "Type1 2"]
    type2 = ["Type2 1", "Type2 2"]
    themes = ["Theme 1", "Theme 2"]
    source = ["Source 1", "Source 2"]
    portal = ["Portal 1", "Portal 2"]
    field_options = {
        "themes": {"create": True},
        "category": {"create": True},
        "type1": {"create": True, "fk": "category"},
        "type2": {"create": True, "fk": "category"},
    }


class ApidaeConstantFieldEventParser(TouristicEventApidaeParser):
    type = "Constant Event"
    themes = ["Theme 1", "Theme 2"]
    source = ["Source 1", "Source 2"]
    portal = ["Portal 1", "Portal 2"]


class EauViveParser(TouristicContentApidaeParser):
    category = "Eau vive"
    type1 = ["Type A", "Type B"]
    type2 = []


class Provider1Parser(TouristicContentApidaeParser):
    category = "Eau vive"
    provider = "Provider1"
    delete = True


class Provider2Parser(TouristicContentApidaeParser):
    category = "Eau vive"
    provider = "Provider2"
    delete = True


class NoProviderParser(TouristicContentApidaeParser):
    category = "Eau vive"
    delete = True


class TestInformationDeskParser(InformationDeskApidaeParser):
    type = "Foo"


class EspritParc(EspritParcParser):
    category = "Miels et produits de la ruche"
    type1 = ["Miel", "Pollen", "Gelée royale, propolis et pollen"]
    type2 = [
        "Hautes Alpes Naturellement",
        "Bienvenue à la ferme",
        "Agriculture biologique",
    ]


class HOT28(TouristicContentTourInSoftParser):
    url = "http://wcf.tourinsoft.com/Syndication/cdt28/xxx/Objects"
    source = "CDT 28"
    category = "Où dormir"
    type1 = "Hôtels"
    type2 = "****"
    portal = "Itinérance"


class HOT28v3(TouristicContentTourInSoftParserV3):
    url = "http://wcf.tourinsoft.com/Syndication/3.0/cdt28/xxx/Objects"
    source = "CDT 28"
    category = "Où dormir"
    type1 = "Hôtels"
    type2 = "****"
    portal = "Itinérance"


class HOT28v3withMedias(TouristicContentTourInSoftParserV3withMedias):
    url = "http://wcf.tourinsoft.com/Syndication/3.0/cdt28/xxx/Objects"
    source = "CDT 28"
    category = "Où dormir"
    type1 = "Hôtels"
    type2 = "****"
    portal = "Itinérance"


class FMA28(TouristicEventTourInSoftParser):
    url = "http://wcf.tourinsoft.com/Syndication/cdt28/xxx/Objects"
    source = "CDT 28"
    type = "Agenda rando"
    portal = "Itinérance"


class FMA28OtherPortal(TouristicEventTourInSoftParser):
    url = "http://wcf.tourinsoft.com/Syndication/cdt28/xxx/Objects"
    source = "CDT 28"
    type = "Agenda rando"
    portal = "Other_portal"
    m2m_aggregate_fields = ["portal"]


class FilenameLEIParser(LEITouristicContentParser):
    filename = "geotrek/tourism/tests/data/LEIContent.xml"
    category = "Restaurant"


class RestaurantALEIParser(LEITouristicContentParser):
    url = "https://apps.tourisme-alsace.info/xml/exploitation/listeproduits.asp"
    category = "Restaurant"
    type1 = "Type 1"
    type2 = "Type 2"
    practical_info = "Practical Info"
    non_fields = {
        "attachments": [
            (
                'CRITERES/Crit[@CLEF_CRITERE="1900604"]',
                'CRITERES/Crit[@CLEF_CRITERE="1900480"]',
            ),
            (
                'CRITERES/Crit[@CLEF_CRITERE="1900421"]',
                'CRITERES/Crit[@CLEF_CRITERE="1900784"]',
            ),
            (
                'CRITERES/Crit[@CLEF_CRITERE="1900268"]',
                'CRITERES/Crit[@CLEF_CRITERE="1900784"]',
            ),
        ],
    }


class RestaurantBLEIParser(LEITouristicContentParser):
    url = "https://apps.tourisme-alsace.info/xml/exploitation/listeproduits.asp"
    category = "Restaurant"
    type1 = "Type 1"
    type2 = "Type 2"
    practical_info = ("CRITERES/Crit", "COMMENTAIREL1")
    non_fields = {}
    practical_info_criteria = [
        "Tox",
    ]

    def filter_practical_info(self, src, val):
        criteres = {}
        crit_elements, coml1 = val
        if coml1:
            criteres["Infos 1"] = coml1
        for elt in crit_elements:
            crit_name, crit_value = self.get_crit_kv(elt)
            if crit_value is not None and crit_name in self.practical_info_criteria:
                if crit_name in criteres.keys():
                    criteres[crit_name].append(crit_value)
                else:
                    criteres[crit_name] = [crit_value]
        result = ""
        for elt in criteres.items():
            formatted_value = ""
            if elt[1] == "" or elt[1] == []:
                continue
            elif isinstance(elt[1], str):
                formatted_value = elt[1]
            elif isinstance(elt[1], list):
                formatted_value = "<br>".join(elt[1])
            result += f"<p><strong>{elt[0]}</strong> : {formatted_value}</p>"
        return result


class EventALEIParser(LEITouristicEventParser):
    url = "https://apps.tourisme-alsace.info/xml/exploitation/listeproduits.asp"
    non_fields = {
        "attachments": [
            (
                'CRITERES/Crit[@CLEF_CRITERE="30000279"]',
                'CRITERES/Crit[@CLEF_CRITERE="30000346"]',
            ),
        ],
    }
    type = "Type event A"


class ParserNoStructureTests(TestCase):
    @mock.patch("geotrek.common.parsers.requests.get")
    def test_filetype_structure_none(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeContent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"

        FileType.objects.create(type="Photographie", structure=None)
        TouristicContentCategoryFactory(label="Eau vive")
        TouristicContentType1Factory(label="Type A")
        TouristicContentType1Factory(label="Type B")
        call_command(
            "import", "geotrek.tourism.tests.test_parsers.EauViveParser", verbosity=0
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicContent.objects.count(), 1)


class ParserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        FileType.objects.create(type="Photographie")

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_create_content_apidae_failed(self, mocked):
        mocked.return_value.status_code = 404
        TouristicContentCategoryFactory(label="Eau vive")
        TouristicContentType1Factory(label="Type A")
        TouristicContentType1Factory(label="Type B")
        with self.assertRaises(CommandError):
            call_command(
                "import",
                "geotrek.tourism.tests.test_parsers.EauViveParser",
                verbosity=2,
            )
        self.assertTrue(mocked.called)

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_create_content_espritparc_failed(self, mocked):
        mocked.return_value.status_code = 404
        category = TouristicContentCategoryFactory(
            label="Miels et produits de la ruche"
        )
        TouristicContentType1Factory(label="Miel", category=category)
        TouristicContentType1Factory(
            label="Gelée royale, propolis et pollen", category=category
        )
        TouristicContentType1Factory(label="Pollen", category=category)
        TouristicContentType1Factory(label="Cire", category=category)
        TouristicContentType2Factory(
            label="Hautes Alpes Naturellement", category=category
        )
        TouristicContentType2Factory(label="Bienvenue à la ferme", category=category)
        TouristicContentType2Factory(label="Agriculture biologique", category=category)
        with self.assertRaises(CommandError):
            call_command(
                "import",
                "geotrek.tourism.tests.test_parsers.EauViveParser",
                verbosity=2,
            )
        self.assertTrue(mocked.called)

    @mock.patch("geotrek.common.parsers.requests.get")
    @override_settings(PARSER_RETRY_SLEEP_TIME=0)
    @mock.patch(
        "geotrek.common.parsers.AttachmentParserMixin.download_attachments", False
    )
    def test_create_content_by_provider(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeContent.json"
            )
            with open(filename) as f:
                return json.load(f)

        def mocked_json2():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeContent2.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        TouristicContentCategoryFactory(label="Eau vive")

        # Parser with provider creates objects with provider
        call_command("import", "geotrek.tourism.tests.test_parsers.Provider1Parser")
        self.assertEqual(TouristicContent.objects.count(), 1)
        self.assertEqual(TouristicContent.objects.first().provider, "Provider1")
        mocked.return_value.json = mocked_json2
        # Parser with provider does not delete other providers' objects
        call_command("import", "geotrek.tourism.tests.test_parsers.Provider2Parser")
        self.assertEqual(TouristicContent.objects.count(), 2)
        call_command("import", "geotrek.tourism.tests.test_parsers.NoProviderParser")
        # Parser with no provider behaves as if all objects are to handle (based on eid only)
        self.assertEqual(TouristicContent.objects.count(), 1)

    @mock.patch("geotrek.common.parsers.requests.get")
    @override_settings(PARSER_RETRY_SLEEP_TIME=0)
    @mock.patch(
        "geotrek.common.parsers.AttachmentParserMixin.download_attachments", False
    )
    def test_create_content_espritparc_retry(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeContent.json"
            )
            with open(filename) as f:
                return json.load(f)

        def side_effect(url, params, auth, code):
            response = requests.Response()
            response.status_code = code
            response.url = url
            if code == 200:
                response.json = mocked_json
            return response

        mocked.side_effect = [
            side_effect(EauViveParser.url, None, None, 503),
            side_effect(EauViveParser.url, None, None, 503),
            side_effect(EauViveParser.url, None, None, 200),
        ]

        TouristicContentCategoryFactory(label="Eau vive")
        TouristicContentType1Factory(label="Type A")
        TouristicContentType1Factory(label="Type B")
        call_command("import", "geotrek.tourism.tests.test_parsers.EauViveParser")
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicContent.objects.count(), 1)

    @mock.patch("geotrek.common.parsers.requests.get")
    @override_settings(PARSER_RETRY_SLEEP_TIME=0)
    def test_create_content_espritparc_retry_fail(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeContent.json"
            )
            with open(filename) as f:
                return json.load(f)

        def side_effect(url, allow_redirects, headers, params):
            response = requests.Response()
            response.status_code = 503
            response.url = url
            return response

        mocked.side_effect = side_effect

        TouristicContentCategoryFactory(label="Eau vive")
        TouristicContentType1Factory(label="Type A")
        TouristicContentType1Factory(label="Type B")
        with self.assertRaisesRegex(
            CommandError,
            f"Failed to download {EauViveParser.url}. HTTP status code 503",
        ):
            call_command("import", "geotrek.tourism.tests.test_parsers.EauViveParser")
            self.assertTrue(mocked.called)

    @mock.patch("geotrek.common.parsers.requests.get")
    @mock.patch("geotrek.common.parsers.requests.head")
    def test_create_content_espritparc_not_fail_type1_does_not_exist(
        self, mocked_head, mocked_get
    ):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "espritparc.json"
            )
            with open(filename) as f:
                return json.load(f)

        filename = os.path.join(os.path.dirname(__file__), "data", "espritparc.json")
        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = mocked_json
        mocked_get.return_value.content = b"Fake image"
        # Mock HEAD
        mocked_head.return_value.status_code = 200
        mocked_head.return_value.headers = {"content-length": 666}
        category = TouristicContentCategoryFactory(
            label="Miels et produits de la ruche"
        )
        TouristicContentType2Factory(
            label="Hautes Alpes Naturellement", category=category
        )
        TouristicContentType2Factory(label="Bienvenue à la ferme", category=category)
        TouristicContentType2Factory(label="Agriculture biologique", category=category)
        output = io.StringIO()
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.EspritParc",
            filename,
            verbosity=2,
            stdout=output,
        )
        self.assertTrue(mocked_get.called)
        self.assertTrue(mocked_head.called)
        self.assertIn(
            "Type 1 'Miel' does not exist for category 'Miels et produits de la ruche'. Please add it,",
            output.getvalue(),
        )

    @mock.patch("geotrek.common.parsers.requests.get")
    @mock.patch("geotrek.common.parsers.requests.head")
    def test_create_content_espritparc_not_fail_type2_does_not_exist(
        self, mocked_head, mocked_get
    ):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "espritparc.json"
            )
            with open(filename) as f:
                return json.load(f)

        filename = os.path.join(os.path.dirname(__file__), "data", "espritparc.json")
        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = mocked_json
        mocked_get.return_value.content = b"Fake image"
        # Mock HEAD
        mocked_head.return_value.status_code = 200
        mocked_head.return_value.headers = {"content-length": 666}
        category = TouristicContentCategoryFactory(
            label="Miels et produits de la ruche"
        )
        TouristicContentType1Factory(label="Miel", category=category)
        TouristicContentType1Factory(
            label="Gelée royale, propolis et pollen", category=category
        )
        TouristicContentType1Factory(label="Pollen", category=category)
        TouristicContentType1Factory(label="Cire", category=category)
        output = io.StringIO()
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.EspritParc",
            filename,
            verbosity=2,
            stdout=output,
        )
        self.assertTrue(mocked_get.called)
        self.assertTrue(mocked_head.called)
        self.assertIn(
            "Type 2 'Bienvenue à la ferme' does not exist for category 'Miels et produits de la ruche'. Please add it",
            output.getvalue(),
        )

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_create_content_apidae(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeContent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"
        category = TouristicContentCategoryFactory(label="Eau vive")
        TouristicContentType1Factory(label="Type A")
        TouristicContentType1Factory(label="Type B")
        call_command(
            "import", "geotrek.tourism.tests.test_parsers.EauViveParser", verbosity=0
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicContent.objects.count(), 1)
        content = TouristicContent.objects.get()
        self.assertEqual(content.eid, "479743")
        self.assertEqual(content.name, "Quey' Raft")
        self.assertEqual(content.description[:27], "Au pied du château médiéval")
        self.assertEqual(content.description_teaser[:24], "Des descentes familiales")
        self.assertEqual(content.contact[:24], "Château Queyras<br>05350")
        self.assertEqual(content.email, "info@queyraft.com")
        self.assertEqual(content.website, "http://www.queyraft.com")
        self.assertEqual(round(content.geom.x), 1000157)
        self.assertEqual(round(content.geom.y), 6413576)
        self.assertEqual(
            content.practical_info[:39], "<b>Ouverture:</b><br>Du 01/05 au 31/10."
        )
        self.assertTrue(
            "<br><b>Capacité totale:</b><br>10<br>" in content.practical_info
        )
        self.assertTrue(
            "><br><b>Services:</b><br>Test, Test2, Test3, Test4<br>"
            in content.practical_info
        )
        self.assertIn(
            "<b>Tarifs:</b><br>A partir de 30 € par personne<br>",
            content.practical_info,
        )
        self.assertIn("<b>Accès:</b><br>TestFr<br>", content.practical_info)
        self.assertTrue(content.published)
        self.assertEqual(content.category, category)
        self.assertListEqual(
            list(content.type1.all().values_list("label", flat=True)),
            ["Type A", "Type B"],
        )
        self.assertQuerySetEqual(content.type2.all(), [])
        self.assertEqual(Attachment.objects.count(), 4)
        self.assertEqual(Attachment.objects.first().content_object, content)

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_no_event_apidae(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeNoEvent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"
        output = io.StringIO()
        call_command(
            "import",
            "geotrek.tourism.parsers.TouristicEventApidaeParser",
            verbosity=2,
            stdout=output,
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicEvent.objects.count(), 0)

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_create_event_apidae(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeEvent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"
        self.assertEqual(TouristicEvent.objects.count(), 0)
        output = io.StringIO()
        call_command(
            "import",
            "geotrek.tourism.parsers.TouristicEventApidaeParser",
            verbosity=2,
            stdout=output,
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicEvent.objects.count(), 1)
        event = TouristicEvent.objects.get()
        self.assertEqual(event.eid, "323154")
        self.assertEqual(event.name, "Cols Réservés 2019 : Montée de Chabre (Laragne)")
        self.assertEqual(event.description[:31], "Le département des Hautes-Alpes")
        self.assertEqual(event.description_teaser[:18], "Une des ascensions")
        self.assertEqual(event.contact[:21], "Châteauneuf de Chabre")
        self.assertEqual(event.email, "LeGrandTim@mail.fr")
        self.assertEqual(event.website, "http://www.LeGrandTim.fr")
        self.assertEqual(round(event.geom.x), 922920)
        self.assertEqual(round(event.geom.y), 6357103)
        self.assertEqual(
            event.practical_info[:38], "<b>Ouverture:</b><br>Mardi 6 août 2019"
        )
        self.assertIn(
            "<b>Capacité totale:</b><br>100 participants<br>", event.practical_info
        )
        self.assertIn(
            "><br><b>Services:</b><br>Le plus grand des services, Un autre grand service<br>",
            event.practical_info,
        )
        self.assertIn(
            "<b>Ouverture:</b><br>Mardi 6 août 2019 de 9h à midi.<br>",
            event.practical_info,
        )
        self.assertIn("<b>Langues Parlées:</b><br>Français<br>", event.practical_info)
        self.assertIn("<b>Accès:</b><br>TestFr<br>", event.practical_info)
        self.assertTrue(event.published)
        self.assertEqual(str(event.start_time), "09:00:00")
        self.assertEqual(event.type.type, "Sports")
        self.assertListEqual(
            list(event.themes.all().values_list("label", flat=True)),
            ["Cyclisme", "Sports cyclistes"],
        )
        self.assertListEqual(
            list(event.organizers.all().values_list("label", flat=True)), ["Toto"]
        )
        self.assertEqual(Attachment.objects.count(), 3)
        self.assertEqual(
            TouristicEventApidaeParser().filter_capacity("capacity", "12"), 12
        )

    def test_filter_capacity_handles_integers(self):
        self.assertEqual(
            TouristicEventApidaeParser().filter_capacity("capacity", 27), 27
        )

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_create_event_apidae_constant_fields(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeEvent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"
        TargetPortalFactory(name="Portal 1")
        TargetPortalFactory(name="Portal 2")
        RecordSourceFactory(name="Source 1")
        RecordSourceFactory(name="Source 2")
        self.assertEqual(TouristicEvent.objects.count(), 0)
        output = io.StringIO()
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.ApidaeConstantFieldEventParser",
            verbosity=2,
            stdout=output,
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicEvent.objects.count(), 1)
        event = TouristicEvent.objects.get()
        self.assertEqual(str(event.type), "Constant Event")
        self.assertQuerySetEqual(
            event.themes.all(), ["Theme 1", "Theme 2"], transform=str
        )
        self.assertQuerySetEqual(
            event.source.all(), ["Source 1", "Source 2"], transform=str
        )
        self.assertQuerySetEqual(
            event.portal.all(), ["Portal 1", "Portal 2"], transform=str
        )

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_create_content_apidae_constant_fields(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeContent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"
        TargetPortalFactory(name="Portal 1")
        TargetPortalFactory(name="Portal 2")
        RecordSourceFactory(name="Source 1")
        RecordSourceFactory(name="Source 2")
        self.assertEqual(TouristicContent.objects.count(), 0)
        output = io.StringIO()
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.ApidaeConstantFieldContentParser",
            verbosity=2,
            stdout=output,
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicContent.objects.count(), 1)
        content = TouristicContent.objects.get()
        self.assertEqual(str(content.category), "Constant Content")
        self.assertQuerySetEqual(
            content.type1.all(), ["Type1 1", "Type1 2"], transform=str
        )
        self.assertQuerySetEqual(
            content.type2.all(), ["Type2 1", "Type2 2"], transform=str
        )
        self.assertQuerySetEqual(
            content.themes.all(), ["Theme 1", "Theme 2"], transform=str
        )
        self.assertQuerySetEqual(
            content.source.all(), ["Source 1", "Source 2"], transform=str
        )
        self.assertQuerySetEqual(
            content.portal.all(), ["Portal 1", "Portal 2"], transform=str
        )

    @mock.patch("geotrek.common.parsers.requests.get")
    @mock.patch("geotrek.common.parsers.requests.head")
    def test_create_esprit(self, mocked_head, mocked_get):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "espritparc.json"
            )
            with open(filename) as f:
                return json.load(f)

        filename = os.path.join(os.path.dirname(__file__), "data", "espritparc.json")
        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = mocked_json
        mocked_get.return_value.content = b"Fake image"
        # Mock HEAD
        mocked_head.return_value.status_code = 200
        mocked_head.return_value.headers = {"content-length": 666}
        category = TouristicContentCategoryFactory(
            label="Miels et produits de la ruche"
        )
        TouristicContentType1Factory(label="Miel", category=category)
        TouristicContentType1Factory(
            label="Gelée royale, propolis et pollen", category=category
        )
        TouristicContentType1Factory(label="Pollen", category=category)
        TouristicContentType1Factory(label="Cire", category=category)
        TouristicContentType2Factory(
            label="Hautes Alpes Naturellement", category=category
        )
        TouristicContentType2Factory(label="Bienvenue à la ferme", category=category)
        TouristicContentType2Factory(label="Agriculture biologique", category=category)
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.EspritParc",
            filename,
            verbosity=0,
        )
        self.assertTrue(mocked_get.called)
        self.assertTrue(mocked_head.called)
        self.assertEqual(TouristicContent.objects.count(), 24)
        content = TouristicContent.objects.all()
        eid = [
            "PDT44",
            "PDT46",
            "PDT47",
            "PDT48",
            "PDT51",
            "PDT52",
            "PDT53",
            "PDT93",
            "PDT94",
            "PDT95",
            "PDT186",
            "PDT260",
            "PDT261",
            "PDT842",
            "PDT471",
            "PDT503",
            "PDT504",
            "PDT505",
            "PDT506",
            "PDT795",
            "PDT797",
            "PDT799",
            "PDT836",
            "PDT837",
        ]
        name = [
            "miel de montagne",
            "miel de haute montagne",
            "miel de printemps d'embrun",
            "gel\xe9e royale de montagne",
            "pollen de montagne",
            "miel de haute montagne bio",
            "miel de for\xeat",
            "miel de pissenlit",
            "miel de haute montagne du valgaudemar",
            "pollen frais de montagne",
            "miel de printemps de l'embrunais",
            "pollen de fleurs de montagne",
            "pain de cire",
            "miel de montagne toutes fleurs",
            "miel cuv\xe9e sp\xe9ciale d'ancelle",
            "miel des ecrins",
        ]
        for one in content:
            self.assertIn(one.eid, eid)
            self.assertIn(one.name.lower(), name)
            self.assertEqual(one.category, category)

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_create_content_tourinsoft_v2(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "tourinsoftContent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"
        category = TouristicContentCategoryFactory(label="Où dormir")
        source = RecordSourceFactory(name="CDT 28")
        portal = TargetPortalFactory(name="Itinérance")
        call_command("import", "geotrek.tourism.tests.test_parsers.HOT28", verbosity=0)
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicContent.objects.count(), 1)
        content = TouristicContent.objects.get()
        self.assertEqual(content.eid, "HOTCEN0280010001")
        self.assertEqual(content.name, "Hôtel du Perche")
        self.assertEqual(content.description[:27], "")
        self.assertEqual(content.description_teaser[:26], "A deux pas du centre ville")
        self.assertEqual(
            content.contact[:73],
            "<strong>Adresse :</strong><br>Rue de la Bruyère<br>28400 NOGENT-LE-ROTROU",
        )
        self.assertEqual(content.email, "hotelduperche@brithotel.fr")
        self.assertEqual(content.website, "http://www.hotel-du-perche.com")
        self.assertEqual(round(content.geom.x), 537329)
        self.assertEqual(round(content.geom.y), 6805504)
        self.assertEqual(
            content.practical_info[:49],
            "<strong>Langues parlées :</strong><br>Anglais<br>",
        )
        self.assertIn("du 01/01/2019 au 21/07/2019", content.practical_info)
        self.assertIn(
            "<strong>Équipements :</strong><br>Bar<br>Parking<br>",
            content.practical_info,
        )
        self.assertTrue(content.published)
        self.assertEqual(content.source.get(), source)
        self.assertEqual(content.portal.get(), portal)
        self.assertEqual(content.category, category)
        self.assertEqual(content.type1.get().label, "Hôtels")
        self.assertEqual(content.type2.get().label, "****")
        self.assertEqual(Attachment.objects.count(), 3)
        self.assertEqual(Attachment.objects.first().content_object, content)

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_create_content_tourinsoft_v3(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "tourinsoftContentV3.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"
        category = TouristicContentCategoryFactory(label="Où dormir")
        source = RecordSourceFactory(name="CDT 28")
        portal = TargetPortalFactory(name="Itinérance")
        call_command(
            "import", "geotrek.tourism.tests.test_parsers.HOT28v3", verbosity=0
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicContent.objects.count(), 2)
        content = TouristicContent.objects.last()
        self.assertEqual(content.eid, "HOTCEN0280010001")
        self.assertEqual(content.name, "Hôtel du Perche")
        self.assertEqual(content.description[:27], "")
        self.assertEqual(content.description_teaser[:26], "A deux pas du centre ville")
        self.assertEqual(
            content.contact[:73],
            "<strong>Adresse :</strong><br>Rue de la Bruyère<br>28400 NOGENT-LE-ROTROU",
        )
        self.assertEqual(content.email, "hotelduperche@brithotel.fr")
        self.assertEqual(content.website, "http://www.hotel-du-perche.com")
        self.assertEqual(round(content.geom.x), 537329)
        self.assertEqual(round(content.geom.y), 6805504)
        self.assertEqual(
            content.practical_info[:49],
            "<strong>Langues parlées :</strong><br>Anglais<br>",
        )
        self.assertIn("du 01/01/2019 au 21/07/2019", content.practical_info)
        self.assertIn(
            "<strong>Équipements :</strong><br>Bar<br>Parking<br>",
            content.practical_info,
        )
        self.assertTrue(content.published)
        self.assertEqual(content.source.get(), source)
        self.assertEqual(content.portal.get(), portal)
        self.assertEqual(content.category, category)
        self.assertEqual(content.type1.get().label, "Hôtels")
        self.assertEqual(content.type2.get().label, "****")
        self.assertEqual(Attachment.objects.count(), 3)
        self.assertEqual(Attachment.objects.first().content_object, content)
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.HOT28v3withMedias",
            verbosity=0,
        )
        self.assertEqual(
            Attachment.objects.filter(
                author="Mairie de Briouze", legend="SteCath800"
            ).count(),
            1,
        )

    @mock.patch("geotrek.common.parsers.requests.get")
    @mock.patch("geotrek.common.parsers.requests.head")
    def test_create_event_tourinsoft(self, mocked_head, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "tourinsoftEvent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"
        # Mock HEAD
        mocked_head.return_value.status_code = 200
        mocked_head.return_value.headers = {"content-length": 666}

        type = TouristicEventTypeFactory(type="Agenda rando")
        source = RecordSourceFactory(name="CDT 28")
        portal = TargetPortalFactory(name="Itinérance")
        call_command("import", "geotrek.tourism.tests.test_parsers.FMA28", verbosity=0)
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicEvent.objects.count(), 1)
        event = TouristicEvent.objects.get()
        self.assertEqual(event.eid, "FMACEN0280060359")
        self.assertEqual(event.name, "Moto cross de Brou")
        self.assertEqual(event.description, "")
        self.assertEqual(event.description_teaser, "")
        self.assertEqual(
            event.contact[:69],
            "<strong>Adresse :</strong><br>Circuit des Tonnes<br>28160 DAMPIERRE-S",
        )
        self.assertEqual(event.email, "moto-club.brou@orange.fr")
        self.assertEqual(event.website, "http://www.mxbrou.com")
        self.assertEqual(round(event.geom.x), 559796)
        self.assertEqual(round(event.geom.y), 6791765)
        self.assertEqual(
            event.practical_info[:61],
            "<strong>Langues parlées :</strong><br>Anglais<br>Allemand<br>",
        )
        self.assertIn(
            "<strong>Équipements :</strong><br>Restauration sur place<br>Sanitaires",
            event.practical_info,
        )
        self.assertTrue(event.published)
        self.assertEqual(event.source.get(), source)
        self.assertEqual(event.portal.get(), portal)
        self.assertEqual(event.type, type)
        self.assertEqual(Attachment.objects.count(), 9)
        self.assertEqual(Attachment.objects.first().content_object, event)
        self.assertEqual(event.begin_date, date(2100, 6, 1))
        self.assertEqual(event.end_date, date(2100, 6, 2))

    @mock.patch("geotrek.common.parsers.requests.get")
    @mock.patch("geotrek.common.parsers.requests.head")
    def test_create_event_multiple_parsers(self, mocked_head, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "tourinsoftEvent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"

        # Mock HEAD
        mocked_head.return_value.status_code = 200
        mocked_head.return_value.headers = {"content-length": 666}

        TouristicEventTypeFactory(type="Agenda rando")
        RecordSourceFactory(name="CDT 28")
        TargetPortalFactory(name="Itinérance")
        TargetPortalFactory(name="Other_portal")

        call_command("import", "geotrek.tourism.tests.test_parsers.FMA28", verbosity=0)

        self.assertEqual(TouristicEvent.objects.count(), 1)
        event = TouristicEvent.objects.get()
        self.assertListEqual(
            list(event.portal.all().values_list("name", flat=True)), ["Itinérance"]
        )
        call_command(
            "import", "geotrek.tourism.tests.test_parsers.FMA28OtherPortal", verbosity=0
        )

        self.assertEqual(TouristicEvent.objects.count(), 1)
        event = TouristicEvent.objects.get()
        self.assertListEqual(
            list(event.portal.all().values_list("name", flat=True)),
            ["Itinérance", "Other_portal"],
        )

    @mock.patch("geotrek.common.parsers.requests.get")
    def test_create_information_desk_apidae(self, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "information_desk.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        InformationDeskTypeFactory.create(label="Foo")

        # Mimetype is included in content in order to check that only non-svg images are saved:
        mocked.return_value.content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR Fake png"
        call_command(
            "import", "geotrek.tourism.tests.test_parsers.TestInformationDeskParser"
        )
        self.assertEqual(InformationDesk.objects.count(), 2)
        information_desk = InformationDesk.objects.get(eid=1)
        self.assertEqual(information_desk.name, "Foo bar")
        self.assertEqual(information_desk.description, "Description")

        with information_desk.photo.open() as f:
            data = f.read()
        self.assertEqual(data, b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR Fake png")

        mocked.return_value.content = b"\xff\xd8\xff\xe0\x00\x10JFIF Fake jpeg"
        call_command(
            "import", "geotrek.tourism.tests.test_parsers.TestInformationDeskParser"
        )
        information_desk.refresh_from_db()
        with information_desk.photo.open() as f:
            data = f.read()
        self.assertEqual(data, b"\xff\xd8\xff\xe0\x00\x10JFIF Fake jpeg")

        mocked.return_value.content = b'<?xml version="1.0"?><svg Fake svg/>'
        call_command(
            "import", "geotrek.tourism.tests.test_parsers.TestInformationDeskParser"
        )
        information_desk.refresh_from_db()
        self.assertFalse(information_desk.photo)

        mocked.return_value.content = b"%PDF-1.4 Fake pdf"
        call_command(
            "import", "geotrek.tourism.tests.test_parsers.TestInformationDeskParser"
        )
        information_desk.refresh_from_db()
        self.assertFalse(information_desk.photo)

        information_desk_2 = InformationDesk.objects.get(eid=2)
        self.assertEqual(information_desk_2.website, None)


class LEIParserTest(TestCase):
    def setUp(self):
        super().setUp()
        FileType.objects.create(type="Photographie")
        TouristicContentCategoryFactory.create(label="Restaurant")
        TouristicContentType1Factory.create(label="Type A")
        TouristicContentType1Factory.create(label="Type B")

    @mock.patch("requests.get")
    def test_fail_lei_url(self, mocked):
        self.x_time = 0

        def mocked_requests_get(*args, **kwargs):
            response = requests.Response()
            response.status_code = 404
            return response

        mocked.side_effect = mocked_requests_get
        with self.assertRaisesRegex(
            CommandError,
            f"Failed to download {RestaurantALEIParser.url}. HTTP status code 404",
        ):
            call_command(
                "import",
                "geotrek.tourism.tests.test_parsers.RestaurantALEIParser",
                verbosity=0,
            )
            self.assertTrue(mocked.called)

    @mock.patch("requests.get")
    def test_create_content_lei_url(self, mocked):
        self.x_time = 0

        def mocked_requests_get(*args, **kwargs):
            response = requests.Response()
            response.status_code = 200
            if self.x_time == 0:
                filename = os.path.join(
                    os.path.dirname(__file__), "data", "LEIContent.xml"
                )
                with open(filename) as f:
                    self.x_time += 1
                    response._content = f.read()
                    return response
            else:
                response._content = b"test"
                return response

        mocked.side_effect = mocked_requests_get

        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.RestaurantALEIParser",
            verbosity=0,
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicContent.objects.count(), 2)
        content = TouristicContent.objects.get(name="Restaurant B")
        self.assertEqual(content.eid, "LEI219006400")
        self.assertEqual(Attachment.objects.count(), 2)
        self.assertEqual(
            Attachment.objects.exclude(legend="").first().legend,
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolo",
        )
        self.assertEqual(Attachment.objects.first().content_object, content)

    def test_create_content_lei_filename(self):
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.FilenameLEIParser",
            verbosity=0,
        )
        self.assertEqual(TouristicContent.objects.count(), 2)

    @mock.patch("requests.get")
    def test_create_content_kv_critere_lei(self, mocked):
        def mocked_requests_get(*args, **kwargs):
            response = requests.Response()
            response.status_code = 200
            filename = os.path.join(os.path.dirname(__file__), "data", "LEIContent.xml")
            with open(filename) as f:
                response._content = f.read()
                return response

        mocked.side_effect = mocked_requests_get

        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.RestaurantBLEIParser",
            verbosity=0,
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicContent.objects.count(), 2)
        content_a = TouristicContent.objects.get(name="Restaurant A")
        self.assertEqual(content_a.eid, "LEI219006399")
        self.assertIn("Commentaire A", content_a.description)
        self.assertEqual(
            "<p><strong>Tox</strong> : Foo : Bar</p>", content_a.practical_info
        )
        content_b = TouristicContent.objects.get(name="Restaurant B")
        self.assertEqual(content_b.eid, "LEI219006400")

    @mock.patch("requests.get")
    def test_create_event_lei(self, mocked):
        self.x_time = 0

        def mocked_requests_get(*args, **kwargs):
            response = requests.Response()
            response.status_code = 200
            if self.x_time == 0:
                filename = os.path.join(
                    os.path.dirname(__file__), "data", "LEIEvent.xml"
                )
                with open(filename) as f:
                    self.x_time += 1
                    response._content = f.read()
                    return response
            else:
                response._content = b"test"
                return response

        mocked.side_effect = mocked_requests_get

        call_command(
            "import", "geotrek.tourism.tests.test_parsers.EventALEIParser", verbosity=0
        )
        self.assertTrue(mocked.called)
        self.assertEqual(TouristicEvent.objects.count(), 1)
        event = TouristicEvent.objects.get()
        self.assertEqual(event.eid, "LEI188003953")
        self.assertEqual(event.name, "Event A")
        self.assertIn("Description A", event.description)
        self.assertEqual(Attachment.objects.count(), 2)
        self.assertEqual(Attachment.objects.first().content_object, event)
        self.assertListEqual(
            list(event.organizers.all().values_list("label", flat=True)),
            ["Resp Event A"],
        )


class TestGeotrekTouristicContentParser(GeotrekTouristicContentParser):
    url = "https://test.fr"

    field_options = {
        "category": {"create": True},
        "structure": {"create": True},
        "themes": {"create": True},
        "source": {"create": True},
        "type1": {"create": True, "fk": "category"},
        "type2": {"create": True, "fk": "category"},
        "geom": {"required": True},
    }


class TestGeotrekTouristicContentCreateCategoriesParser(GeotrekTouristicContentParser):
    url = "https://test.fr"
    create_categories = True


class TestGeotrekTouristicEventParser(GeotrekTouristicEventParser):
    url = "https://test.fr"
    field_options = {
        "source": {"create": True},
        "type": {
            "create": True,
        },
        "geom": {"required": True},
        "structure": {"create": True},
    }


class TestGeotrekInformationDeskParser(GeotrekInformationDeskParser):
    url = "https://test.fr"

    field_options = {
        "type": {
            "create": True,
        },
        "geom": {"required": True},
    }


class TouristicContentGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "tourism"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("tourism", "structure.json"),
            ("tourism", "touristiccontent_category.json"),
            ("tourism", "touristiccontent_themes.json"),
            ("tourism", "sources.json"),
            ("tourism", "sources.json"),
            ("tourism", "touristiccontent_category.json"),
            ("tourism", "touristiccontent_ids.json"),
            ("tourism", "touristiccontent.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.TestGeotrekTouristicContentCreateCategoriesParser",
            verbosity=0,
        )
        self.assertEqual(TouristicContent.objects.count(), 2)
        touristic_content = TouristicContent.objects.all().first()
        self.assertEqual(str(touristic_content.category), "Sorties")
        self.assertEqual(str(touristic_content.type1.first()), "Ane")
        self.assertEqual(str(touristic_content.name), "Balad'âne")
        self.assertEqual(str(touristic_content.structure), "Struct1")
        self.assertEqual(
            str(touristic_content.source.first().name), "Une source numero 2"
        )
        self.assertAlmostEqual(touristic_content.geom.x, 568112.6362873032, places=5)
        self.assertAlmostEqual(touristic_content.geom.y, 6196929.676669887, places=5)
        self.assertEqual(Attachment.objects.count(), 3)

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
    def test_create_create_categories(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("tourism", "structure.json"),
            ("tourism", "touristiccontent_category.json"),
            ("tourism", "touristiccontent_themes.json"),
            ("tourism", "sources.json"),
            ("tourism", "sources.json"),
            ("tourism", "touristiccontent_category.json"),
            ("tourism", "touristiccontent_ids.json"),
            ("tourism", "touristiccontent.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.TestGeotrekTouristicContentParser",
            verbosity=0,
        )
        self.assertEqual(TouristicContent.objects.count(), 2)
        touristic_content = TouristicContent.objects.all().first()
        self.assertEqual(str(touristic_content.category), "Sorties")
        self.assertEqual(str(touristic_content.name), "Balad'âne")
        self.assertAlmostEqual(touristic_content.geom.x, 568112.6362873032, places=5)
        self.assertAlmostEqual(touristic_content.geom.y, 6196929.676669887, places=5)
        self.assertEqual(Attachment.objects.count(), 3)


class TouristicEventGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "tourism"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("tourism", "structure.json"),
            ("tourism", "touristicevent_type.json"),
            ("tourism", "sources.json"),
            ("tourism", "sources.json"),
            ("tourism", "touristicevent_ids.json"),
            ("tourism", "touristicevent.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.TestGeotrekTouristicEventParser",
            verbosity=0,
        )
        self.assertEqual(TouristicEvent.objects.count(), 2)
        touristic_event = TouristicEvent.objects.all().first()
        self.assertEqual(str(touristic_event.type), "Spectacle")
        self.assertEqual(str(touristic_event.structure), "Struct1")
        self.assertEqual(str(touristic_event.name), "Autrefois le Couserans")
        self.assertEqual(
            str(touristic_event.source.first().name), "Une source numero 2"
        )
        self.assertAlmostEqual(touristic_event.geom.x, 548907.5259389633, places=5)
        self.assertAlmostEqual(touristic_event.geom.y, 6208918.713349126, places=5)


class InformationDeskGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "tourism"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("geotrek.common.parsers.AttachmentParserMixin.download_attachment")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
    def test_create(self, mocked_download_attachment, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("tourism", "informationdesk_ids.json"),
            ("tourism", "informationdesk.json"),
        ]
        self.mock_download = 0

        def mocked_download(*args, **kwargs):
            if self.mock_download > 0:
                return None
            self.mock_download += 1
            return b"boo"

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_download_attachment.side_effect = mocked_download
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.TestGeotrekInformationDeskParser",
            verbosity=0,
        )
        self.assertEqual(InformationDesk.objects.count(), 3)
        information_desk = InformationDesk.objects.all().first()
        self.assertEqual(str(information_desk.type), "Relais d'information")
        self.assertEqual(str(information_desk.name), "Foo")
        self.assertAlmostEqual(information_desk.geom.x, 573013.9272605104, places=5)
        self.assertAlmostEqual(information_desk.geom.y, 6276967.321705549, places=5)
        self.assertEqual(str(information_desk.photo), "")
        self.assertEqual(
            InformationDesk.objects.exclude(photo="").first().photo.read(), b"boo"
        )


class TestInformationDeskOpenStreetMapParser(InformationDeskOpenStreetMapParser):
    type = "Foo"
    tags = [{"amenity": "ranger_station"}]
    default_fields_values = {"name": "test_default"}


@override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
class OpenStreetMapInformationDeskParserTests(TestCase):
    @classmethod
    @mock.patch("geotrek.common.parsers.requests.get")
    def import_information_desk(cls, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "information_desk_OSM.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json

        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.TestInformationDeskOpenStreetMapParser",
        )

    @classmethod
    def setUpTestData(cls):
        cls.type = InformationDeskTypeFactory.create(label="Foo")
        FileType.objects.create(type="Photographie")

        cls.import_information_desk()

        cls.objects = InformationDesk.objects

    def test_create_information_desk_OSM(self):
        self.assertEqual(self.objects.count(), 4)

    def test_InformationDesk_eid_filter_OSM(self):
        information_desks_eids = (
            self.objects.order_by("eid").all().values_list("eid", flat=True)
        )
        self.assertListEqual(list(information_desks_eids), ["N1", "N2", "R4", "W3"])
        self.assertNotEqual(information_desks_eids, ["1", "2", "3", "4"])

    def test_get_tag_info_existing_tag_OSM(self):
        information_desk = self.objects.get(eid="N1")
        self.assertEqual(information_desk.phone, "0754347899")

        information_desk2 = self.objects.get(eid="N2")
        self.assertEqual(information_desk2.phone, "0754347899")

    def test_get_tag_info_no_tag_OSM(self):
        information_desk = self.objects.get(eid="W3")
        self.assertEqual(information_desk.phone, None)

    def test_InformationDesk_street_filter_housenumber_and_street_OSM(self):
        information_desk = self.objects.get(eid="N1")
        self.assertEqual(information_desk.street, "5 rue des chênes")

    def test_InformationDesk_street_filter_street_OSM(self):
        information_desk = self.objects.get(eid="N2")
        self.assertEqual(information_desk.street, "rue des chênes")

    def test_InformationDesk_street_filter_None_OSM(self):
        information_desk = self.objects.get(eid="W3")
        self.assertEqual(information_desk.street, None)

    def test_geom_point_to_point_OSM(self):
        information_desk = self.objects.get(eid="N1")
        self.assertAlmostEqual(information_desk.geom.coords[0], 673775.507, places=2)
        self.assertAlmostEqual(information_desk.geom.coords[1], 6260613.093, places=2)

    def test_geom_way_to_point_OSM(self):
        information_desk = self.objects.get(eid="W3")
        self.assertAlmostEqual(information_desk.geom.coords[0], 639380.854, places=2)
        self.assertAlmostEqual(information_desk.geom.coords[1], 6256494.451, places=2)

    def test_geom_relation_to_point_OSM(self):
        information_desk = self.objects.get(eid="R4")
        self.assertAlmostEqual(information_desk.geom.coords[0], -5898321.244, places=2)
        self.assertAlmostEqual(information_desk.geom.coords[1], 12807160.659, places=2)

    def test_default_fields(self):
        information_desk = self.objects.get(eid="N1")
        self.assertEqual(information_desk.name, "test:fr")

        information_desk2 = self.objects.get(eid="R4")
        self.assertEqual(information_desk2.name, "test_default")

    def test_translated_fields(self):
        # default language
        information_desk = self.objects.get(eid="N1")
        self.assertEqual(information_desk.name, "test:fr")
        information_desk2 = self.objects.get(eid="N2")
        self.assertEqual(information_desk2.name, "test")

        # translation language
        information_desk = self.objects.get(eid="N1")
        self.assertEqual(information_desk.name_en, "test:en")
        information_desk2 = self.objects.get(eid="W3")
        self.assertEqual(information_desk2.name_en, None)


class TestOpenStreetMapTouristicContentParser(OpenStreetMapTouristicContentParser):
    category = "Foo"
    type1 = ["test type1.1", "test type1.2", "test type1.3"]
    type2 = "test type2"
    themes = ["test theme1", "test theme2"]
    portal = ["test portal1", "test portal2"]
    source = ["test source1", "test source2"]
    tags = [{"tourism": "hotel"}]
    default_fields_values = {"name": "test_default"}
    field_options = {
        "themes": {"create": True},
        "source": {"create": True},
        "type2": {"create": True, "fk": "category"},
    }


@override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
class OpenStreetMapTouristicContentParserTests(TestCase):
    @classmethod
    @mock.patch("requests.get")
    def import_touristic_content(cls, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "touristic_content_OSM.json"
            )
            with open(filename) as f:
                return json.load(f)

        def mocked_polygons_valid(decode):
            wkt_polygon = "SRID=4326;POLYGON ((3.976107 45.32012, 4.032755 45.32012, 4.032755 45.345841, 3.976107 45.345841, 3.976107 45.32012), (3.990655 45.326602, 4.020352 45.326602, 4.020352 45.340489, 3.990655 45.340489, 3.990655 45.326602))"
            return wkt_polygon

        def mocked_polygons_non_valid(decode):
            wkt_polygon = "SRID=4326;MULTIPOLYGON (((3.976107 45.32012, 4.032755 45.32012, 4.032755 45.345841, 3.976107 45.345841, 3.976107 45.32012)), ((3.990655 45.326602, 4.020352 45.326602, 4.020352 45.340489, 3.990655 45.340489, 3.990655 45.326602)))"
            return wkt_polygon

        mock_overpass = mock.Mock()
        mock_overpass.status_code = 200
        mock_overpass.json = mocked_json

        mock_polygons_valid = mock.Mock()
        mock_polygons_valid.status_code = 200
        mock_polygons_valid.content.decode = mocked_polygons_valid

        mock_polygons_missing = mock.Mock()
        mock_polygons_missing.status_code = 500
        mock_polygons_missing.content.decode = mocked_polygons_valid

        mock_polygons_non_valid = mock.Mock()
        mock_polygons_non_valid.status_code = 200
        mock_polygons_non_valid.content.decode = mocked_polygons_non_valid

        mocked.side_effect = [
            mock_overpass,
            mock_polygons_valid,
            mock_polygons_missing,
            mock_polygons_non_valid,
        ]

        output = io.StringIO()
        call_command(
            "import",
            "geotrek.tourism.tests.test_parsers.TestOpenStreetMapTouristicContentParser",
            stdout=output,
        )

        cls.output = output.getvalue()

    @classmethod
    def setUpTestData(cls):
        cls.category = TouristicContentCategoryFactory.create(label="Foo")
        FileType.objects.create(type="Photographie")
        TouristicContentType1Factory.create(label="test type1.1", category=cls.category)
        TouristicContentType1Factory.create(label="test type1.2", category=cls.category)
        TargetPortalFactory(name="test portal1")
        TargetPortalFactory(name="test portal2")

        cls.import_touristic_content()

        cls.objects = TouristicContent.objects

    def test_create_touristic_content_OSM(self):
        self.assertEqual(self.objects.count(), 6)

    def test_type1_touristic_content_OSM(self):
        touristic_content = self.objects.first()
        self.assertEqual(touristic_content.type1.all().count(), 2)
        self.assertEqual(touristic_content.type1.first().label, "test type1.1")
        warning = (
            "Type1 'test type1.3' n'existe pas dans Geotrek-Admin. Merci de l'ajouter"
        )
        self.assertIn(warning, self.output)

    def test_type2_touristic_content_OSM(self):
        touristic_content = self.objects.first()
        self.assertEqual(touristic_content.type2.all().count(), 1)
        self.assertEqual(touristic_content.type2.first().label, "test type2")
        warning = "Type2 'test type2' n'existait pas dans Geotrek-Admin. Il a été créé automatiquement"
        self.assertIn(warning, self.output)

    def test_themes_touristic_content_OSM(self):
        touristic_content = self.objects.first()
        self.assertEqual(touristic_content.themes.all().count(), 2)
        self.assertEqual(touristic_content.themes.first().label, "test theme1")
        warnings = [
            "Thème 'test theme1' n'existait pas dans Geotrek-Admin. Il a été créé automatiquement",
            "Thème 'test theme2' n'existait pas dans Geotrek-Admin. Il a été créé automatiquement",
        ]
        self.assertIn(warnings[0], self.output)
        self.assertIn(warnings[1], self.output)

    def test_portal_touristic_content_OSM(self):
        touristic_content = self.objects.first()
        self.assertEqual(touristic_content.portal.all().count(), 2)
        self.assertEqual(touristic_content.portal.first().name, "test portal1")

    def test_source_touristic_content_OSM(self):
        touristic_content = self.objects.first()
        self.assertEqual(touristic_content.source.all().count(), 2)
        self.assertEqual(touristic_content.source.first().name, "test source1")
        warnings = [
            "Source Des Fiches 'test source1' n'existait pas dans Geotrek-Admin. Il a été créé automatiquement",
            "Source Des Fiches 'test source2' n'existait pas dans Geotrek-Admin. Il a été créé automatiquement",
        ]
        self.assertIn(warnings[0], self.output)
        self.assertIn(warnings[1], self.output)

    def test_filter_contact(self):
        touristic_content = self.objects.get(eid="N1")
        self.assertEqual(touristic_content.contact, "")

        touristic_content = self.objects.get(eid="W2")
        contact = "0786535787<br>Montmorillon"
        self.assertEqual(touristic_content.contact, contact)

        touristic_content = self.objects.get(eid="W3")
        contact = "0786535787<br>86500, Montmorillon"
        self.assertEqual(touristic_content.contact, contact)

        touristic_content = self.objects.get(eid="R4")
        contact = "0786535787<br>46 rue des tournesols"
        self.assertEqual(touristic_content.contact, contact)

    def test_geom_point(self):
        touristic_content = self.objects.get(eid="N1")
        self.assertEqual(type(touristic_content.geom), Point)
        self.assertAlmostEqual(touristic_content.geom.x, 673775.507, places=2)
        self.assertAlmostEqual(touristic_content.geom.y, 6260613.093, places=2)

    def test_geom_way_line(self):
        touristic_content = self.objects.get(eid="W2")
        self.assertEqual(type(touristic_content.geom), LineString)
        self.assertEqual(len(touristic_content.geom), 2)
        self.assertAlmostEqual(touristic_content.geom[0][0], 639373.356, places=2)
        self.assertAlmostEqual(touristic_content.geom[0][1], 6256499.938, places=2)

    def test_geom_way_polygon(self):
        touristic_content = self.objects.get(eid="W3")
        self.assertEqual(type(touristic_content.geom), Polygon)
        self.assertEqual(len(touristic_content.geom[0]), 5)
        self.assertAlmostEqual(touristic_content.geom[0][0][0], 639373.356, places=2)
        self.assertAlmostEqual(touristic_content.geom[0][0][1], 6256499.938, places=2)

    def test_geom_relation_polygon(self):
        touristic_content = self.objects.get(eid="R4")
        self.assertEqual(type(touristic_content.geom), Polygon)
        self.assertEqual(touristic_content.geom.num_interior_rings, 1)
        self.assertEqual(len(touristic_content.geom[0]), 5)
        self.assertEqual(len(touristic_content.geom[1]), 5)
        self.assertAlmostEqual(touristic_content.geom[0][0][0], 776475.184, places=2)
        self.assertAlmostEqual(touristic_content.geom[0][0][1], 6469444.353, places=2)
        self.assertAlmostEqual(touristic_content.geom[1][0][0], 777605.887, places=2)
        self.assertAlmostEqual(touristic_content.geom[1][0][1], 6470178.359, places=2)

    def test_geom_relation_point(self):
        touristic_content = self.objects.get(eid="R5")
        self.assertEqual(type(touristic_content.geom), Point)
        self.assertAlmostEqual(touristic_content.geom.x, 770813.800, places=2)
        self.assertAlmostEqual(touristic_content.geom.y, 6055930.570, places=2)

    def test_geom_relation_non_valid_polygon(self):
        touristic_content = self.objects.get(eid="R6")
        self.assertEqual(type(touristic_content.geom), Polygon)
        self.assertEqual(touristic_content.geom.num_interior_rings, 0)
        self.assertEqual(len(touristic_content.geom[0]), 5)
        self.assertAlmostEqual(touristic_content.geom[0][0][0], 776475.184, places=2)
        self.assertAlmostEqual(touristic_content.geom[0][0][1], 6469444.353, places=2)
