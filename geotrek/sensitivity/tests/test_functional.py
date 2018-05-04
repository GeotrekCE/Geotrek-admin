from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from geotrek.common.tests import CommonTest
from geotrek.sensitivity.models import SensitiveArea
from geotrek.sensitivity.factories import (SensitiveAreaFactory, SpeciesFactory, SportPracticeFactory,
                                           RegulatorySensitiveAreaFactory)
from mapentity.factories import SuperUserFactory


class SensitiveAreaViewsTests(CommonTest):
    model = SensitiveArea
    modelfactory = SensitiveAreaFactory
    userfactory = SuperUserFactory

    def setUp(self):
        translation.deactivate()
        super(SensitiveAreaViewsTests, self).setUp()

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'species': SpeciesFactory.create().pk,
            'geom': '{"type": "Polygon", "coordinates":[[[0, 0], [0, 1], [1, 0], [0, 0]]]}',
            'structure': str(self.user.profile.structure.pk),
        }


class RegulatorySensitiveAreaViewsTests(CommonTest):
    model = SensitiveArea
    modelfactory = RegulatorySensitiveAreaFactory
    userfactory = SuperUserFactory

    def setUp(self):
        translation.deactivate()
        super(RegulatorySensitiveAreaViewsTests, self).setUp()

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'name': 'Test',
            'practices': [SportPracticeFactory.create().pk],
            'geom': '{"type": "Polygon", "coordinates":[[[0, 0], [0, 1], [1, 0], [0, 0]]]}',
            'structure': str(self.user.profile.structure.pk),
        }

    def _get_add_url(self):
        return self.model.get_add_url() + '?category=2'

    def test_crud_status(self):
        if self.model is None:
            return  # Abstract test should not run

        self.login()

        obj = self.modelfactory()

        response = self.client.get(obj.get_list_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(obj.get_detail_url().replace(str(obj.pk), '1234567890'))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(obj.get_detail_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(obj.get_update_url())
        self.assertEqual(response.status_code, 200)

        self._post_update_form(obj)

        response = self.client.get(obj.get_delete_url())
        self.assertEqual(response.status_code, 200)

        url = obj.get_detail_url()
        obj.delete()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        self._post_add_form()

        # Test to update without login
        self.logout()

        obj = self.modelfactory()

        response = self.client.get(self.model.get_add_url() + '?category=2')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(obj.get_update_url())
        self.assertEqual(response.status_code, 302)
