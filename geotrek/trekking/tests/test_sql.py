from django.test import TestCase

from django.db import connection

from geotrek.common.tests.factories import LabelFactory
from geotrek.common.tests.mixins import dictfetchall
from geotrek.trekking.tests.factories import TrekFactory


class SQLViewsTest(TestCase):
    def test_trekking(self):
        trek = TrekFactory.create(name="foo bar")
        label_1 = LabelFactory.create(name='enux', name_fr='frux')
        label_2 = LabelFactory.create()
        trek.labels.add(label_1, label_2)
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM v_treks")
            datas = dictfetchall(cur)

        sql_trek_dict = datas[0]

        self.assertEqual(sql_trek_dict['Labels en'], 'enux,Label')
        self.assertEqual(sql_trek_dict['Labels fr'], 'frux,_')
        self.assertEqual(sql_trek_dict['Structure'], 'My structure')
        self.assertEqual(sql_trek_dict['Name en'], 'foo bar')
