# -*- encoding: utf-8 -*-

from datetime import date
import io
import json
import mock
import os

from django.test import TestCase
from django.core.management import call_command

from geotrek.common.factories import RecordSourceFactory, TargetPortalFactory
from geotrek.common.models import Attachment, FileType
from geotrek.common.tests import TranslationResetMixin
from geotrek.tourism.factories import (TouristicContentCategoryFactory, TouristicContentType1Factory,
                                       TouristicContentType2Factory, TouristicEventTypeFactory)
from geotrek.tourism.models import TouristicContent, TouristicEvent
from geotrek.tourism.parsers import (TouristicContentApidaeParser, EspritParcParser,
                                     TouristicContentTourInSoftParser, TouristicEventTourInSoftParser)


class EauViveParser(TouristicContentApidaeParser):
    category = u"Eau vive"
    type1 = [u"Type A", u"Type B"]
    type2 = []


class EspritParc(EspritParcParser):
    category = u"Miels et produits de la ruche"
    type1 = [u"Miel", u"Pollen", u"Gelée royale, propolis et pollen"]
    type2 = [u"Hautes Alpes Naturellement", u"Bienvenue à la ferme", u"Agriculture biologique"]


class HOT28(TouristicContentTourInSoftParser):
    url = "http://wcf.tourinsoft.com/Syndication/cdt28/xxx/Objects"
    source = "CDT 28"
    category = u"Où dormir"
    type1 = u"Hôtels"
    type2 = u"****"
    portal = u"Itinérance"


class FMA28(TouristicEventTourInSoftParser):
    url = "http://wcf.tourinsoft.com/Syndication/cdt28/xxx/Objects"
    source = "CDT 28"
    type = u"Agenda rando"


class ParserTests(TranslationResetMixin, TestCase):
    @mock.patch('requests.get')
    def test_create_content_apidae(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'apidaeContent.json')
            with io.open(filename, 'r', encoding='utf8') as f:
                return json.load(f)
        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        FileType.objects.create(type=u"Photographie")
        category = TouristicContentCategoryFactory(label=u"Eau vive")
        TouristicContentType1Factory(label=u"Type A")
        TouristicContentType1Factory(label=u"Type B")
        call_command('import', 'geotrek.tourism.tests.test_parsers.EauViveParser', verbosity=0)
        self.assertEqual(TouristicContent.objects.count(), 1)
        content = TouristicContent.objects.get()
        self.assertEqual(content.eid, u"479743")
        self.assertEqual(content.name, u"Quey' Raft")
        self.assertEqual(content.description[:27], u"Au pied du château médiéval")
        self.assertEqual(content.description_teaser[:24], u"Des descentes familiales")
        self.assertEqual(content.contact[:24], u"Château Queyras<br>05350")
        self.assertEqual(content.email, u"info@queyraft.com")
        self.assertEqual(content.website, u"http://www.queyraft.com")
        self.assertEqual(round(content.geom.x), 1000157)
        self.assertEqual(round(content.geom.y), 6413576)
        self.assertEqual(content.practical_info[:39], "<b>Ouverture:</b><br>Du 01/05 au 31/10.")
        self.assertTrue(u"<br><b>Capacité totale:</b><br>10<br>" in content.practical_info)
        self.assertTrue(u"><br><b>Services:</b><br>Test, Test2, Test3, Test4<br>" in content.practical_info)
        self.assertTrue(content.published)
        self.assertEqual(content.category, category)
        self.assertQuerysetEqual(
            content.type1.all(),
            ['<TouristicContentType1: Type A>', '<TouristicContentType1: Type B>']
        )
        self.assertQuerysetEqual(content.type2.all(), [])
        self.assertEqual(Attachment.objects.count(), 3)
        self.assertEqual(Attachment.objects.first().content_object, content)

    @mock.patch('requests.get')
    def test_filetype_structure_none(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'apidaeContent.json')
            with io.open(filename, 'r', encoding='utf8') as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        FileType.objects.create(type=u"Photographie", structure=None)
        TouristicContentCategoryFactory(label=u"Eau vive")
        TouristicContentType1Factory(label=u"Type A")
        TouristicContentType1Factory(label=u"Type B")
        call_command('import', 'geotrek.tourism.tests.test_parsers.EauViveParser', verbosity=0)
        self.assertEqual(TouristicContent.objects.count(), 1)

    @mock.patch('requests.get')
    def test_create_event_apidae(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'apidaeEvent.json')
            with io.open(filename, 'r', encoding='utf8') as f:
                return json.load(f)
        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        FileType.objects.create(type=u"Photographie")
        self.assertEqual(TouristicEvent.objects.count(), 0)
        call_command('import', 'geotrek.tourism.parsers.TouristicEventApidaeParser', verbosity=0)
        self.assertEqual(TouristicEvent.objects.count(), 1)
        event = TouristicEvent.objects.get()
        self.assertEqual(event.eid, u"323154")
        self.assertEqual(event.name, u"Cols Réservés 2019 : Montée de Chabre (Laragne)")
        self.assertEqual(event.description[:31], u"Le département des Hautes-Alpes")
        self.assertEqual(event.description_teaser[:18], u"Une des ascensions")
        self.assertEqual(event.contact[:21], u"Châteauneuf de Chabre")
        self.assertEqual(event.email, u"LeGrandTim@mail.fr")
        self.assertEqual(event.website, u"http://www.LeGrandTim.fr")
        self.assertEqual(round(event.geom.x), 922920)
        self.assertEqual(round(event.geom.y), 6357103)
        self.assertEqual(event.practical_info[:38], u"<b>Ouverture:</b><br>Mardi 6 août 2019")
        self.assertIn(u"><br><b>Services:</b><br>Le plus grand des services, Un autre grand service<br>",
                      event.practical_info)
        self.assertTrue(event.published)
        self.assertEqual(event.organizer, u'Toto')
        self.assertEqual(str(event.meeting_time), '09:00:00')
        self.assertEqual(event.type.type, 'Sports')
        self.assertQuerysetEqual(
            event.themes.all(),
            ['<Theme: Cyclisme>', '<Theme: Sports cyclistes>']
        )
        self.assertEqual(Attachment.objects.count(), 3)

    @mock.patch('requests.get')
    def test_create_esprit(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'espritparc.json')
            with io.open(filename, 'r', encoding='utf8') as f:
                return json.load(f)

        filename = os.path.join(os.path.dirname(__file__), 'data', 'espritparc.json')
        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        FileType.objects.create(type=u"Photographie")
        category = TouristicContentCategoryFactory(label=u"Miels et produits de la ruche")
        TouristicContentType1Factory(label=u"Miel", category=category)
        TouristicContentType1Factory(label=u"Gelée royale, propolis et pollen", category=category)
        TouristicContentType1Factory(label=u"Pollen", category=category)
        TouristicContentType1Factory(label=u"Cire", category=category)
        TouristicContentType2Factory(label=u"Hautes Alpes Naturellement", category=category)
        TouristicContentType2Factory(label=u"Bienvenue à la ferme", category=category)
        TouristicContentType2Factory(label=u"Agriculture biologique", category=category)
        call_command('import', 'geotrek.tourism.tests.test_parsers.EspritParc', filename, verbosity=0)
        self.assertEqual(TouristicContent.objects.count(), 24)
        content = TouristicContent.objects.all()
        eid = [
            u"PDT44", u"PDT46", u"PDT47", u"PDT48", u"PDT51", u"PDT52", u"PDT53", u"PDT93", u"PDT94", u"PDT95",
            u"PDT186", u"PDT260", u"PDT261", u"PDT842", u"PDT471", u"PDT503", u"PDT504", u"PDT505", u"PDT506",
            u"PDT795", u"PDT797", u"PDT799", u"PDT836", u"PDT837"
        ]
        name = [
            u"miel de montagne", u"miel de haute montagne", u"miel de printemps d'embrun",
            u"gel\xe9e royale de montagne", u"pollen de montagne", u"miel de haute montagne bio", u"miel de for\xeat",
            u"miel de pissenlit", u"miel de haute montagne du valgaudemar", u"pollen frais de montagne",
            u"miel de printemps de l'embrunais", u"pollen de fleurs de montagne", u"pain de cire",
            u"miel de montagne toutes fleurs", u"miel cuv\xe9e sp\xe9ciale d'ancelle", u"miel des ecrins"

        ]
        for one in content:
            self.assertIn(one.eid, eid)
            self.assertIn(one.name.lower(), name)
            self.assertEqual(one.category, category)

    @mock.patch('requests.get')
    def test_create_content_tourinsoft(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'tourinsoftContent.json')
            with io.open(filename, 'r', encoding='utf8') as f:
                return json.load(f)
        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        FileType.objects.create(type=u"Photographie")
        category = TouristicContentCategoryFactory(label=u"Où dormir")
        source = RecordSourceFactory(name=u"CDT 28")
        portal = TargetPortalFactory(name=u"Itinérance")
        call_command('import', 'geotrek.tourism.tests.test_parsers.HOT28', verbosity=0)
        self.assertEqual(TouristicContent.objects.count(), 1)
        content = TouristicContent.objects.get()
        self.assertEqual(content.eid, u"HOTCEN0280010001")
        self.assertEqual(content.name, u"Hôtel du Perche")
        self.assertEqual(content.description[:27], u"")
        self.assertEqual(content.description_teaser[:26], u"A deux pas du centre ville")
        self.assertEqual(content.contact[:69], u"<strong>Adresse :</strong><br/>Rue de la Bruyère<br/>NOGENT-LE-ROTROU")
        self.assertEqual(content.email, u"hotelduperche@brithotel.fr")
        self.assertEqual(content.website, u"http://www.hotel-du-perche.com")
        self.assertEqual(round(content.geom.x), 537329)
        self.assertEqual(round(content.geom.y), 6805504)
        self.assertEqual(content.practical_info[:51], u"<strong>Langues parlées :</strong><br/>Anglais<br/>")
        self.assertTrue(u"<strong>Équipements :</strong><br/>Bar<br/>Parking<br/>" in content.practical_info)
        self.assertTrue(content.published)
        self.assertEqual(content.source.get(), source)
        self.assertEqual(content.portal.get(), portal)
        self.assertEqual(content.category, category)
        self.assertEqual(content.type1.get().label, u"Hôtels")
        self.assertEqual(content.type2.get().label, u"****")
        self.assertEqual(Attachment.objects.count(), 3)
        self.assertEqual(Attachment.objects.first().content_object, content)

    @mock.patch('requests.get')
    def test_create_event_tourinsoft(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'tourinsoftEvent.json')
            with io.open(filename, 'r', encoding='utf8') as f:
                return json.load(f)
        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        FileType.objects.create(type=u"Photographie")
        type = TouristicEventTypeFactory(type=u"Agenda rando")
        source = RecordSourceFactory(name="CDT 28")
        call_command('import', 'geotrek.tourism.tests.test_parsers.FMA28', verbosity=0)
        self.assertEqual(TouristicEvent.objects.count(), 1)
        event = TouristicEvent.objects.get()
        self.assertEqual(event.eid, u"FMACEN0280060359")
        self.assertEqual(event.name, u"Moto cross de Brou")
        self.assertEqual(event.description, u"")
        self.assertEqual(event.description_teaser, u"")
        self.assertEqual(event.contact[:69], u"<strong>Adresse :</strong><br/>Circuit des Tonnes<br/>DAMPIERRE-SOUS-")
        self.assertEqual(event.email, u"moto-club.brou@orange.fr")
        self.assertEqual(event.website, u"http://www.mxbrou.com")
        self.assertEqual(round(event.geom.x), 559796)
        self.assertEqual(round(event.geom.y), 6791765)
        self.assertTrue(event.published)
        self.assertEqual(event.source.get(), source)
        self.assertEqual(event.type, type)
        self.assertEqual(Attachment.objects.count(), 9)
        self.assertEqual(Attachment.objects.first().content_object, event)
        self.assertEqual(event.begin_date, date(2019, 6, 1))
        self.assertEqual(event.end_date, date(2019, 6, 2))
