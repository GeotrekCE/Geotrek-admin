from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.test import TestCase
from django.template import Template, Context
from django.template.exceptions import TemplateSyntaxError
from django.utils import translation
from django.utils.timezone import make_aware, utc

from geotrek.tourism.factories import TouristicEventFactory

from datetime import datetime, timedelta
import json
import os
import shutil


class ValueListTest(TestCase):
    def test_empty_list_should_show_none(self):
        translation.deactivate()
        out = Template(
            '{% load mapentity_tags %}'
            '{% valuelist items %}'
        ).render(Context({
            'items': []
        }))
        self.assertEqual(out.strip(), '<span class="none">None</span>')

    def test_simple_usage_outputs_list_of_items(self):
        out = Template(
            '{% load mapentity_tags %}'
            '{% valuelist items %}'
        ).render(Context({
            'items': ['blah']
        }))
        self.assertEqual(out.strip(), """<ul>\n    <li>blah</li>\n    </ul>""")

    def test_can_specify_field_to_be_used(self):
        obj = TouristicEventFactory.create(name='blah')
        out = Template(
            '{% load mapentity_tags %}'
            '{% valuelist items field="name" %}'
        ).render(Context({
            'items': [obj]
        }))
        self.assertIn("""title="blah">blah</a></li>""", out.strip())

    def test_can_specify_an_enumeration4(self):
        out = Template(
            '{% load mapentity_tags %}'
            '{% valuelist items enumeration=True %}'
        ).render(Context({
            'items': range(1, 4)
        }))
        self.assertIn('<li><span class="enumeration-value">A.&nbsp;</span>1</li>', out)
        self.assertIn('<li><span class="enumeration-value">B.&nbsp;</span>2</li>', out)
        self.assertIn('<li><span class="enumeration-value">C.&nbsp;</span>3</li>', out)

    def test_can_specify_an_enumeration30(self):
        out = Template(
            '{% load mapentity_tags %}'
            '{% valuelist items enumeration=True %}'
        ).render(Context({
            'items': range(1, 30)
        }))
        self.assertIn('<li><span class="enumeration-value">AA.&nbsp;</span>1</li>', out)
        self.assertIn('<li><span class="enumeration-value">AZ.&nbsp;</span>26</li>', out)
        self.assertIn('<li><span class="enumeration-value">BA.&nbsp;</span>27</li>', out)
        self.assertIn('<li><span class="enumeration-value">BB.&nbsp;</span>28</li>', out)

    def test_can_specify_an_enumeration300(self):
        out = Template(
            '{% load mapentity_tags %}'
            '{% valuelist items enumeration=True %}'
        ).render(Context({
            'items': range(1, 678)
        }))
        self.assertIn('<li><span class="enumeration-value">AAA.&nbsp;</span>1</li>', out)
        self.assertIn('<li><span class="enumeration-value">AAZ.&nbsp;</span>26</li>', out)
        self.assertIn('<li><span class="enumeration-value">ABA.&nbsp;</span>27</li>', out)
        self.assertIn('<li><span class="enumeration-value">ABB.&nbsp;</span>28</li>', out)
        self.assertIn('<li><span class="enumeration-value">BAA.&nbsp;</span>677</li>', out)


class SmartIncludeTest(TestCase):
    def test_smart_include_no_argument(self):
        with self.assertRaisesRegex(TemplateSyntaxError, "'smart_include' tag requires one argument"):
            Template(
                '{% load mapentity_tags %}'
                '{% smart_include %}'
            ).render(Context())

    def test_smart_include_no_quotes(self):
        with self.assertRaisesRegex(TemplateSyntaxError,
                                    "'smart_include' tag's viewname argument should be in quotes"):
            Template(
                '{% load mapentity_tags %}'
                '{% smart_include test %}'
            ).render(Context())


class LatLngBoundsTest(TestCase):
    def test_latlngbound_null(self):
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object|latlngbounds }}'
        ).render(Context({'object': None}))
        self.assertEqual('null', out)

    def test_latlngbound_object(self):
        object_event = TouristicEventFactory.create()
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object|latlngbounds }}'
        ).render(Context({'object': object_event}))
        json_out = json.loads(out)
        self.assertAlmostEqual(json_out[0][0], -5.9838563092087576)
        self.assertAlmostEqual(json_out[0][1], -1.363081210117898)
        self.assertAlmostEqual(json_out[1][0], -5.9838563092087576)
        self.assertAlmostEqual(json_out[1][1], -1.363081210117898)


class FieldVerboseNameTest(TestCase):
    def test_field_no_field_but_verbose_name_field(self):
        object_event = TouristicEventFactory.create()
        setattr(object_event, 'do_not_exist_verbose_name', "test")
        template = Template(
            '{% load mapentity_tags %}'
            '{{ object|verbose:"do_not_exist" }}'
        ).render(Context({'object': object_event}))
        self.assertEqual(template, "test")

    def test_field_verbose_name_field_does_not_exist(self):
        object_event = TouristicEventFactory.create()
        with self.assertRaisesRegex(FieldDoesNotExist, "TouristicEvent has no field named 'do_not_exist'"):
            Template(
                '{% load mapentity_tags %}'
                '{{ object|verbose:"do_not_exist" }}'
            ).render(Context({'object': object_event}))


class MediasFallbackExistTest(TestCase):
    def setUp(self):
        os.mkdir(os.path.join('var', 'media', 'testx3'))
        with open(os.path.join('var', 'media', 'testx3', 'logo-login.png'), 'wb') as f:
            f.write(b'')

    def test_media_static_fallback_exist(self):
        out = Template(
            '{% load mapentity_tags %}'
            '{% media_static_fallback "testx3/logo-login.png" "images/logo-login.png" %}'
        ).render(Context())
        self.assertEqual('/media/testx3/logo-login.png', out)

    def test_media_static_fallback_path_exist(self):
        out = Template(
            '{% load mapentity_tags %}'
            '{% media_static_fallback_path "testx3/logo-login.png" "images/logo-login.png" %}'
        ).render(Context())
        self.assertEqual('%s/testx3/logo-login.png' % settings.MEDIA_ROOT, out)

    def tearDown(self):
        shutil.rmtree(os.path.join('var', 'media', 'testx3'))


class TimeSinceTest(TestCase):
    def setUp(self):
        translation.activate('en')

    def test_time_since_years(self):
        date = make_aware(datetime.now() - timedelta(days=800), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertEqual('2 years ago', out)

    def test_time_since_year(self):
        date = make_aware(datetime.now() - timedelta(days=366), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertEqual('1 year ago', out)

    def test_time_since_weeks(self):
        date = make_aware(datetime.now() - timedelta(days=15), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('2 weeks ago', out)

    def test_time_since_week(self):
        date = make_aware(datetime.now() - timedelta(days=13), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('1 week ago', out)

    def test_time_since_days(self):
        date = make_aware(datetime.now() - timedelta(days=3), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('3 days ago', out)

    def test_time_since_day(self):
        date = make_aware(datetime.now() - timedelta(days=1), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('1 day ago', out)

    def test_time_since_hours(self):
        date = make_aware(datetime.now() - timedelta(hours=4), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('4 hours ago', out)

    def test_time_since_hour(self):
        date = make_aware(datetime.now() - timedelta(hours=1), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('1 hour ago', out)

    def test_time_since_minutes(self):
        date = make_aware(datetime.now() - timedelta(minutes=3), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('3 minutes ago', out)

    def test_time_since_minute(self):
        date = make_aware(datetime.now() - timedelta(minutes=1), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('1 minute ago', out)

    def test_time_since_seconds(self):
        date = make_aware(datetime.now() - timedelta(seconds=15), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('just a few seconds ago', out)

    def test_time_since_now(self):
        date = make_aware(datetime.now(), utc)
        object_event = TouristicEventFactory.create(begin_date=date)
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context({'object': object_event}))
        self.assertIn('just a few seconds ago', out)

    def test_time_since_wrong_object(self):
        out = Template(
            '{% load mapentity_tags %}'
            '{{ object.begin_date|timesince }}'
        ).render(Context())
        self.assertIn('', out)
