import datetime

from django.test import TestCase
from django.test.utils import override_settings

from django.utils.timezone import utc, make_aware

from geotrek.common.tests.factories import AttachmentFactory, LabelFactory, RecordSourceFactory, TargetPortalFactory
from geotrek.common.tests import TranslationResetMixin

from geotrek.authent.tests.factories import StructureFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.tests.factories import POIFactory, TrekFactory
from geotrek.cirkwi.serializers import timestamp

from geotrek.trekking import urls  # NOQA


class CirkwiTests(TranslationResetMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory.create()
        cls.creation = make_aware(datetime.datetime(2014, 1, 1), utc)
        cls.trek = TrekFactory.create(published=True, paths=[cls.path])
        cls.trek.date_insert = cls.creation
        cls.trek.save()
        TrekFactory.create(published=False, paths=[cls.path])
        cls.portal_1 = TargetPortalFactory()
        cls.portal_2 = TargetPortalFactory()
        cls.source_1 = RecordSourceFactory()
        cls.source_2 = RecordSourceFactory()
        cls.trek.portal.set([cls.portal_1, cls.portal_2])
        cls.trek.source.set([cls.source_1, cls.source_2])
        POIFactory.create(published=False, paths=[cls.path])
        cls.label_1 = LabelFactory(advice_fr="Lorep ipsum 1 fr", advice_en="Lorep ipsum 1 en")
        cls.label_2 = LabelFactory(advice_fr="Lorep ipsum 2 fr", advice_en="Lorep ipsum 2 en")
        cls.trek.labels.set([cls.label_1, cls.label_2])

    def setUp(self):
        self.poi = POIFactory.create(published=True, paths=[self.path])
        self.poi.date_insert = self.creation
        self.poi.save()

    def test_export_circuits(self):
        response = self.client.get('/api/cirkwi/circuits.xml')
        self.assertEqual(response.status_code, 200)
        attrs = {
            'pk': self.trek.pk,
            'title': self.trek.name,
            'date_update': timestamp(self.trek.date_update),
            'n': self.trek.description.replace('<p>description ', '').replace('</p>', ''),
            'poi_pk': self.poi.pk,
            'poi_title': self.poi.name,
            'poi_date_update': timestamp(self.poi.date_update),
            'poi_description': self.poi.description.replace('<p>', '').replace('</p>', ''),
        }
        self.assertXMLEqual(
            response.content.decode(),
            '<?xml version="1.0" encoding="utf8"?>\n'
            '<circuits version="2">'
            '<circuit date_creation="1388534400" date_modification="{date_update}" id_circuit="{pk}">'
            '<informations>'
            '<information langue="en">'
            '<titre>{title}</titre>'
            '<description>Description teaser\n\nDescription</description>'
            '<informations_complementaires>'
            '<information_complementaire><titre>Departure</titre><description>Departure</description></information_complementaire>'
            '<information_complementaire><titre>Arrival</titre><description>Arrival</description></information_complementaire>'
            '<information_complementaire><titre>Ambiance</titre><description>Ambiance</description></information_complementaire>'
            '<information_complementaire><titre>Access</titre><description>Access</description></information_complementaire>'
            '<information_complementaire><titre>Accessibility infrastructure</titre><description>Accessibility infrastructure</description></information_complementaire>'
            '<information_complementaire><titre>Advised parking</titre><description>Advised parking</description></information_complementaire>'
            '<information_complementaire><titre>Public transport</titre><description>Public transport</description></information_complementaire>'
            '<information_complementaire><titre>Advice</titre><description>Advice</description></information_complementaire>'
            '<information_complementaire><titre>Label</titre><description>Lorep ipsum 1 en</description></information_complementaire>'
            '<information_complementaire><titre>Label</titre><description>Lorep ipsum 2 en</description></information_complementaire>'
            '</informations_complementaires>'
            '</information>'
            '</informations>'
            '<distance>141</distance>'
            '<locomotions><locomotion duree="5400"></locomotion></locomotions>'
            '<fichier_trace url="http://testserver/api/en/treks/{pk}/trek.kml"></fichier_trace>'
            '<tracking_information>'
            '<portals>'
            f'<portal id="{self.portal_1.pk}" nom="{self.portal_1.name}">'
            '</portal>'
            f'<portal id="{self.portal_2.pk}" nom="{self.portal_2.name}">'
            '</portal>'
            '</portals>'
            '<sources>'
            f'<source id="{self.source_1.pk}" nom="{self.source_1.name}">'
            '</source>'
            f'<source id="{self.source_2.pk}" nom="{self.source_2.name}">'
            '</source>'
            '</sources>'
            f'<structure id="{self.trek.structure.pk}" nom="My structure"></structure>'
            '</tracking_information>'
            '<pois>'
            '<poi date_creation="1388534400" date_modification="{poi_date_update}" id_poi="{poi_pk}">'
            '<informations>'
            '<information langue="en"><titre>POI</titre><description>Description</description></information>'
            '</informations>'
            '<adresse><position><lat>46.5</lat><lng>3.0</lng></position></adresse>'
            '</poi>'
            '</pois>'
            '</circuit>'
            '</circuits>'.format(**attrs))

    def test_export_pois(self):
        response = self.client.get('/api/cirkwi/pois.xml')
        self.assertEqual(response.status_code, 200)
        attrs = {
            'pk': self.poi.pk,
            'title': self.poi.name,
            'description': self.poi.description.replace('<p>', '').replace('</p>', ''),
            'date_update': timestamp(self.poi.date_update),
        }
        self.assertXMLEqual(
            response.content.decode(),
            '<?xml version="1.0" encoding="utf8"?>\n'
            '<pois version="2">'
            '<poi id_poi="{pk}" date_modification="{date_update}" date_creation="1388534400">'
            '<informations>'
            '<information langue="en"><titre>{title}</titre><description>{description}</description></information>'
            '</informations>'
            '<adresse><position><lat>46.5</lat><lng>3.0</lng></position></adresse>'
            '</poi>'
            '</pois>'.format(**attrs))

    def test_export_pois_with_attachments(self):
        attachment = AttachmentFactory.create(content_object=self.poi, attachment_file=get_dummy_uploaded_image())
        response = self.client.get('/api/cirkwi/pois.xml')
        self.assertEqual(response.status_code, 200)
        attrs = {
            'pk': self.poi.pk,
            'title': self.poi.name,
            'description': self.poi.description.replace('<p>', '').replace('</p>', ''),
            'date_update': timestamp(self.poi.date_update),
            'legend': attachment.legend,
            'picture': f'http://testserver{self.poi.resized_pictures[0][1].url}'
        }
        self.assertXMLEqual(
            response.content.decode(),
            '<?xml version="1.0" encoding="utf8"?>\n'
            '<pois version="2">'
            '<poi id_poi="{pk}" date_modification="{date_update}" date_creation="1388534400">'
            '<informations>'
            '<information langue="en"><titre>{title}</titre><description>{description}</description>'
            '<medias><images><image><legende>{legend}</legende><url>{picture}</url></image></images></medias></information>'
            '</informations>'
            '<adresse><position><lat>46.5</lat><lng>3.0</lng></position></adresse>'
            '</poi>'
            '</pois>'.format(**attrs)
        )

    def test_export_circuits_with_attachments(self):
        attachment = AttachmentFactory.create(content_object=self.trek, attachment_file=get_dummy_uploaded_image())
        self.poi.delete()
        response = self.client.get('/api/cirkwi/circuits.xml')
        self.assertEqual(response.status_code, 200)

        attrs = {
            'pk': self.trek.pk,
            'title': self.trek.name,
            'date_update': timestamp(self.trek.date_update),
            'n': self.trek.description.replace('<p>description ', '').replace('</p>', ''),
            'legend': attachment.legend,
            'picture': f'http://testserver{self.trek.resized_pictures[0][1].url}'
        }
        self.assertXMLEqual(
            response.content.decode(),
            '<?xml version="1.0" encoding="utf8"?>\n'
            '<circuits version="2">'
            '<circuit date_creation="1388534400" date_modification="{date_update}" id_circuit="{pk}">'
            '<informations>'
            '<information langue="en">'
            '<titre>{title}</titre>'
            '<description>Description teaser\n\nDescription</description>'
            '<medias><images><image><legende>{legend}</legende><url>{picture}</url></image></images></medias>'
            '<informations_complementaires>'
            '<information_complementaire><titre>Departure</titre><description>Departure</description></information_complementaire>'
            '<information_complementaire><titre>Arrival</titre><description>Arrival</description></information_complementaire>'
            '<information_complementaire><titre>Ambiance</titre><description>Ambiance</description></information_complementaire>'
            '<information_complementaire><titre>Access</titre><description>Access</description></information_complementaire>'
            '<information_complementaire><titre>Accessibility infrastructure</titre><description>Accessibility infrastructure</description></information_complementaire>'
            '<information_complementaire><titre>Advised parking</titre><description>Advised parking</description></information_complementaire>'
            '<information_complementaire><titre>Public transport</titre><description>Public transport</description></information_complementaire>'
            '<information_complementaire><titre>Advice</titre><description>Advice</description></information_complementaire>'
            '<information_complementaire><titre>Label</titre><description>Lorep ipsum 1 en</description></information_complementaire>'
            '<information_complementaire><titre>Label</titre><description>Lorep ipsum 2 en</description></information_complementaire>'
            '</informations_complementaires>'
            '</information>'
            '</informations>'
            '<distance>141</distance>'
            '<locomotions><locomotion duree="5400"></locomotion></locomotions>'
            '<fichier_trace url="http://testserver/api/en/treks/{pk}/trek.kml"></fichier_trace>'
            '<tracking_information>'
            '<portals>'
            f'<portal id="{self.portal_1.pk}" nom="{self.portal_1.name}">'
            '</portal>'
            f'<portal id="{self.portal_2.pk}" nom="{self.portal_2.name}">'
            '</portal>'
            '</portals>'
            '<sources>'
            f'<source id="{self.source_1.pk}" nom="{self.source_1.name}">'
            '</source>'
            f'<source id="{self.source_2.pk}" nom="{self.source_2.name}">'
            '</source>'
            '</sources>'
            f'<structure id="{self.trek.structure.pk}" nom="My structure"></structure>'
            '</tracking_information>'
            '</circuit>'
            '</circuits>'.format(**attrs))

    @override_settings(PUBLISHED_BY_LANG=False)
    def test_export_pois_without_langs(self):
        response = self.client.get('/api/cirkwi/pois.xml')
        self.assertEqual(response.status_code, 200)
        attrs = {
            'pk': self.poi.pk,
            'title': self.poi.name,
            'description': self.poi.description.replace('<p>', '').replace('</p>', ''),
            'date_update': timestamp(self.poi.date_update),
        }
        self.assertXMLEqual(
            response.content.decode(),
            '<?xml version="1.0" encoding="utf8"?>\n'
            '<pois version="2">'
            '<poi id_poi="{pk}" date_modification="{date_update}" date_creation="1388534400">'
            '<informations>'
            '<information langue="en"><titre>{title}</titre><description>{description}</description></information>'
            '<information langue="es"><titre>{title}</titre><description>{description}</description></information>'
            '<information langue="fr"><titre>{title}</titre><description>{description}</description></information>'
            '<information langue="it"><titre>{title}</titre><description>{description}</description></information>'
            '</informations>'
            '<adresse><position><lat>46.5</lat><lng>3.0</lng></position></adresse>'
            '</poi>'
            '</pois>'.format(**attrs))

    def test_trek_filter_portals(self):
        portal = TargetPortalFactory.create()
        self.trek.portal.add(portal)

        # We found one trek with the portal
        response = self.client.get(f'/api/cirkwi/circuits.xml?portals={portal.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLNotEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                          '<circuits version="2"/>')
        other_portal = TargetPortalFactory.create()
        # We found no treks with the other portal's id
        response = self.client.get(f'/api/cirkwi/circuits.xml?portals={other_portal.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                       '<circuits version="2"/>')

        # We found treks when we ask for the other portal's id and portal's id
        response = self.client.get(f'/api/cirkwi/circuits.xml?portals={other_portal.pk},{portal.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLNotEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                          '<circuits version="2"/>')

    def test_trek_filter_structures(self):
        structure = StructureFactory.create()
        self.trek.structure = structure
        self.trek.save()

        # We found one trek with the structure
        response = self.client.get(f'/api/cirkwi/circuits.xml?structures={structure.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLNotEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                          '<circuits version="2"/>')
        other_structure = StructureFactory.create()
        # We found no treks with the other structure's id
        response = self.client.get(f'/api/cirkwi/circuits.xml?structures={other_structure.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                       '<circuits version="2"/>')

        response = self.client.get(f'/api/cirkwi/circuits.xml?structures={other_structure.pk},{structure.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLNotEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                          '<circuits version="2"/>')

    def test_poi_filter_structures(self):
        structure = StructureFactory.create()
        self.poi.structure = structure
        self.poi.save()

        # We found one trek with the structure
        response = self.client.get(f'/api/cirkwi/pois.xml?structures={structure.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLNotEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                          '<pois version="2"/>')
        other_structure = StructureFactory.create()
        # We found no treks with the other structure's id
        response = self.client.get(f'/api/cirkwi/pois.xml?structures={other_structure.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                       '<pois version="2"/>')

        response = self.client.get(f'/api/cirkwi/pois.xml?structures={other_structure.pk},{structure.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLNotEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                          '<pois version="2"/>')

        response = self.client.get(f'/api/cirkwi/pois.xml?structures={other_structure.pk}&structures={structure.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertXMLNotEqual(response.content.decode(), '<?xml version="1.0" encoding="utf8"?>\n'
                                                          '<pois version="2"/>')
