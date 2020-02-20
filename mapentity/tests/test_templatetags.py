from django.test import TestCase
from django.template import Template, Context
from django.utils import translation

from geotrek.tourism.factories import TouristicEventFactory


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
