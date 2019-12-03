import os

from unittest import mock

from django.contrib.auth.models import Permission
from django.utils import translation
from django.utils.translation import ugettext as _
from django.conf import settings

# Workaround https://code.djangoproject.com/ticket/22865
from geotrek.common.models import FileType  # NOQA

from mapentity.factories import SuperUserFactory
from mapentity.tests import MapEntityTest, MapEntityLiveTest

from geotrek.authent.factories import StructureFactory
from geotrek.authent.tests import AuthentFixturesTest


class TranslationResetMixin(object):
    def setUp(self):
        translation.deactivate()
        super(TranslationResetMixin, self).setUp()


class CommonTest(AuthentFixturesTest, TranslationResetMixin, MapEntityTest):
    api_prefix = '/api/en/'

    def get_bad_data(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            return {'topology': 'doh!'}, _('Topology is not valid.')
        else:
            return {'geom': 'doh!'}, _('Invalid geometry value.')

    def test_structure_is_set(self):
        if not hasattr(self.model, 'structure'):
            return
        self.login()
        response = self.client.post(self._get_add_url(), self.get_good_data())
        self.assertEqual(response.status_code, 302)
        obj = self.model.objects.last()
        self.assertEqual(obj.structure, self.user.profile.structure)

    def test_structure_is_not_changed_without_permission(self):
        if not hasattr(self.model, 'structure'):
            return
        self.login()
        structure = StructureFactory()
        self.assertNotEqual(structure, self.user.profile.structure)
        self.assertFalse(self.user.has_perm('authent.can_bypass_structure'))
        obj = self.modelfactory.create(structure=structure)
        result = self.client.post(obj.get_update_url(), self.get_good_data())
        self.assertEqual(result.status_code, 302)
        self.assertEqual(self.model.objects.first().structure, structure)
        self.logout()

    def test_structure_is_changed_with_permission(self):
        if not hasattr(self.model, 'structure'):
            return
        self.login()
        perm = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm)
        structure = StructureFactory()
        self.assertNotEqual(structure, self.user.profile.structure)
        obj = self.modelfactory.create(structure=structure)
        data = self.get_good_data()
        data['structure'] = self.user.profile.structure.pk
        result = self.client.post(obj.get_update_url(), data)
        self.assertEqual(result.status_code, 302)
        self.assertEqual(self.model.objects.first().structure, self.user.profile.structure)
        self.logout()

    def test_set_structure_with_permission(self):
        if not hasattr(self.model, 'structure'):
            return
        self.login()
        perm = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm)
        structure = StructureFactory()
        self.assertNotEqual(structure, self.user.profile.structure)
        data = self.get_good_data()
        data['structure'] = self.user.profile.structure.pk
        response = self.client.post(self._get_add_url(), data)
        self.assertEqual(response.status_code, 302)
        obj = self.model.objects.last()
        self.assertEqual(obj.structure, self.user.profile.structure)
        self.logout()

    def test_detail_other_language(self):
        if self.model is None:
            return  # Abstract test should not run

        self.login()

        obj = self.modelfactory()

        response = self.client.get('%s?lang=fr' % obj.get_detail_url())
        self.assertEqual(response.status_code, 200)


class CommonLiveTest(MapEntityLiveTest):
    @mock.patch('mapentity.helpers.requests')
    def test_map_image_other_language(self, mock_requests):
        if self.model is None:
            return  # Abstract test should not run

        SuperUserFactory.create(username='Superuser', password='booh')
        self.client.login(username='Superuser', password='booh')

        obj = self.modelfactory.create(geom='POINT(0 0)')

        # Initially, map image does not exists
        image_path = obj.get_map_image_path()
        if os.path.exists(image_path):
            os.remove(image_path)
        self.assertFalse(os.path.exists(image_path))

        # Mock Screenshot response
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = b'*' * 100

        response = self.client.get(obj.map_image_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists(image_path))

        mapimage_url = '%s%s?context&lang=fr' % (self.live_server_url, obj.get_detail_url())
        screenshot_url = 'http://0.0.0.0:8001/?url=%s' % mapimage_url
        url_called = mock_requests.get.call_args_list[0]
        self.assertTrue(url_called.startswith(screenshot_url))
