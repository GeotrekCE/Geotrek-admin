from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from geotrek.authent.models import Structure
from geotrek.common.tests import CommonLiveTest, CommonTest
from geotrek.diving.models import Dive
from geotrek.diving.factories import DiveFactory, DivingManagerFactory, PracticeFactory

from mapentity.factories import SuperUserFactory


class DiveViewsTests(CommonTest):
    model = Dive
    modelfactory = DiveFactory
    userfactory = DivingManagerFactory

    def setUp(self):
        super(DiveViewsTests, self).setUp()

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'structure': Structure.objects.first().pk,
            'name_en': 'test',
            'practice': PracticeFactory.create().pk,
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }

    def test_services_on_treks_do_not_exist(self):
        self.login()
        self.modelfactory.create()
        response = self.client.get(reverse('diving:dive_service_geojson', kwargs={'lang': translation.get_language(), 'pk': 0}))
        self.assertEqual(response.status_code, 404)

    def test_services_on_treks_not_public(self):
        self.login()
        dive = self.modelfactory.create(published=False)
        response = self.client.get(reverse('diving:dive_service_geojson', kwargs={'lang': translation.get_language(), 'pk': dive.pk}))
        self.assertEqual(response.status_code, 404)

    def test_pois_on_treks_do_not_exist(self):
        self.login()
        self.modelfactory.create()
        response = self.client.get(reverse('diving:dive_poi_geojson', kwargs={'lang': translation.get_language(), 'pk': 0}))
        self.assertEqual(response.status_code, 404)

    def test_pois_on_treks_not_public(self):
        self.login()
        dive = self.modelfactory.create(published=False)
        response = self.client.get(reverse('diving:dive_poi_geojson', kwargs={'lang': translation.get_language(), 'pk': dive.pk}))
        self.assertEqual(response.status_code, 404)


class DiveViewsLiveTests(CommonLiveTest):
    model = Dive
    modelfactory = DiveFactory
    userfactory = SuperUserFactory
