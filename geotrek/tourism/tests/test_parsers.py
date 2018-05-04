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
from geotrek.tourism.parsers import TouristicContentSitraParser


class EauViveParser(TouristicContentSitraParser):
    category = "Eau vive"
    type1 = ["Type A", "Type B"]
    type2 = []


class ParserTests(TranslationResetMixin, TestCase):
    @mock.patch('requests.get')
    def test_create(self, mocked):
        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'sitra.json')
            with io.open(filename, 'r', encoding='utf8') as f:
                return json.load(f)
        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b''
        FileType.objects.create(type="Photographie")
        category = TouristicContentCategoryFactory(label="Eau vive")
        TouristicContentTypeFactory(label="Type A")
        TouristicContentTypeFactory(label="Type B")
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
        self.assertTrue(content.published)
        self.assertEqual(content.category, category)
        self.assertQuerysetEqual(
            content.type1.all(),
            ['<TouristicContentType: Type A>', '<TouristicContentType: Type B>']
        )
        self.assertQuerysetEqual(content.type2.all(), [])
        self.assertEqual(Attachment.objects.count(), 3)
        self.assertEqual(Attachment.objects.first().content_object, content)
