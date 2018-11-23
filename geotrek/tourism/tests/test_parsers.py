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
from geotrek.tourism.models import TouristicContent
from geotrek.tourism.parsers import TouristicContentApidaeParser, EspritParcParser


class EauViveParser(TouristicContentApidaeParser):
    category = "Eau vive"
    type1 = ["Type A", "Type B"]
    type2 = []


class EspritParc(EspritParcParser):
    category = "Miels et produits de la ruche"
    type1 = ["Miel", "Pollen", "Gelée royale, propolis et pollen"]
    type2 = ["Hautes Alpes Naturellement", "Bienvenue à la ferme", "Agriculture biologique"]


class ParserTests(TranslationResetMixin, TestCase):
    @mock.patch('requests.get')
    def test_create(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'apidae.json')
            with io.open(filename, 'r', encoding='utf8') as f:
                return json.load(f)
        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b''
        FileType.objects.create(type="Photographie")
        category = TouristicContentCategoryFactory(label="Eau vive")
        TouristicContentTypeFactory(label="Type A", in_list=1)
        TouristicContentTypeFactory(label="Type B", in_list=1)
        call_command('import', 'geotrek.tourism.tests.test_parsers.EauViveParser', verbosity=0)
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
        self.assertEqual(content.practical_info[:39], "<b>Ouverture:</b><br>Du 01/05 au 31/10.")
        self.assertTrue("<br><b>Capacité totale:</b><br>10<br>" in content.practical_info)
        self.assertTrue("><br><b>Services:</b><br>Test, Test2, Test3, Test4<br>" in content.practical_info)
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
    def test_create_esprit(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'espritparc.json')
            with io.open(filename, 'rb') as f:
                return json.load(f)

        filename = os.path.join(os.path.dirname(__file__), 'data', 'espritparc.json')
        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b''
        FileType.objects.create(type="Photographie")
        category = TouristicContentCategoryFactory(label="Miels et produits de la ruche")
        TouristicContentTypeFactory(label="Miel", in_list=1, category=category)
        TouristicContentTypeFactory(label="Gelée royale, propolis et pollen", in_list=1, category=category)
        TouristicContentTypeFactory(label="Pollen", in_list=1, category=category)
        TouristicContentTypeFactory(label="Cire", in_list=1, category=category)
        TouristicContentTypeFactory(label="Hautes Alpes Naturellement", in_list=2, category=category)
        TouristicContentTypeFactory(label="Bienvenue à la ferme", in_list=2, category=category)
        TouristicContentTypeFactory(label="Agriculture biologique", in_list=2, category=category)
        call_command('import', 'geotrek.tourism.tests.test_parsers.EspritParc', filename, verbosity=0)
        self.assertEqual(TouristicContent.objects.count(), 24)
        content = TouristicContent.objects.all()
        eid = [
            "PDT44", "PDT46", "PDT47", "PDT48", "PDT51", "PDT52", "PDT53", "PDT93", "PDT94", "PDT95",
            "PDT186", "PDT260", "PDT261", "PDT842", "PDT471", "PDT503", "PDT504", "PDT505", "PDT506",
            "PDT795", "PDT797", "PDT799", "PDT836", "PDT837"
        ]
        name = [
            "miel de montagne", "miel de haute montagne", "miel de printemps d'embrun",
            "gel\xe9e royale de montagne", "pollen de montagne", "miel de haute montagne bio", "miel de for\xeat",
            "miel de pissenlit", "miel de haute montagne du valgaudemar", "pollen frais de montagne",
            "miel de printemps de l'embrunais", "pollen de fleurs de montagne", "pain de cire",
            "miel de montagne toutes fleurs", "miel cuv\xe9e sp\xe9ciale d'ancelle", "miel des ecrins"

        ]
        for one in content:
            self.assertIn(one.eid, eid)
            self.assertIn(one.name.lower(), name)
            self.assertEqual(one.category, category)
