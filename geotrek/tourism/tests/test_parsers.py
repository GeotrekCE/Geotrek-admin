# -*- encoding: utf-8 -*-

import io
import json
import mock
import os

from django.test import TestCase
from django.core.management import call_command

from geotrek.common.models import Attachment, FileType
from geotrek.common.tests import TranslationResetMixin
from geotrek.tourism.factories import TouristicContentCategoryFactory, TouristicContentTypeFactory
from geotrek.tourism.models import TouristicContent, TouristicEvent
from geotrek.tourism.parsers import TouristicContentApidaeParser, EspritParcParser


class EauViveParser(TouristicContentApidaeParser):
    category = u"Eau vive"
    type1 = [u"Type A", u"Type B"]
    type2 = []


class EspritParc(EspritParcParser):
    category = u"Miels et produits de la ruche"
    type1 = [u"Miel", u"Pollen", u"Gelée royale, propolis et pollen"]
    type2 = [u"Hautes Alpes Naturellement", u"Bienvenue à la ferme", u"Agriculture biologique"]


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
        TouristicContentTypeFactory(label=u"Type A", in_list=1)
        TouristicContentTypeFactory(label=u"Type B", in_list=1)
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
            ['<TouristicContentType: Type A>', '<TouristicContentType: Type B>']
        )
        self.assertQuerysetEqual(content.type2.all(), [])
        self.assertEqual(Attachment.objects.count(), 3)
        self.assertEqual(Attachment.objects.first().content_object, content)

    @mock.patch('requests.get')
    def test_create_event_apidae(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'apidaeEvent.json')
            with io.open(filename, 'r', encoding='utf8') as f:
                return json.load(f)
        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        FileType.objects.create(type=u"Photographie")
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
        TouristicContentTypeFactory(label=u"Miel", in_list=1, category=category)
        TouristicContentTypeFactory(label=u"Gelée royale, propolis et pollen", in_list=1, category=category)
        TouristicContentTypeFactory(label=u"Pollen", in_list=1, category=category)
        TouristicContentTypeFactory(label=u"Cire", in_list=1, category=category)
        TouristicContentTypeFactory(label=u"Hautes Alpes Naturellement", in_list=2, category=category)
        TouristicContentTypeFactory(label=u"Bienvenue à la ferme", in_list=2, category=category)
        TouristicContentTypeFactory(label=u"Agriculture biologique", in_list=2, category=category)
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
