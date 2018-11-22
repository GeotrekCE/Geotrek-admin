# -*- encoding: utf-8 -*-
from django.utils import translation
from django.utils.translation import ugettext as _

# Workaround https://code.djangoproject.com/ticket/22865
from geotrek.common.models import FileType  # NOQA

from mapentity.tests import MapEntityTest

from geotrek.authent.factories import StructureFactory
from geotrek.authent.tests import AuthentFixturesTest


class TranslationResetMixin(object):
    def setUp(self):
        translation.deactivate()
        super(TranslationResetMixin, self).setUp()


class CommonTest(AuthentFixturesTest, TranslationResetMixin, MapEntityTest):
    api_prefix = '/api/en/'

    def get_bad_data(self):
        return {'topology': 'doh!'}, _('Topology is not valid.')

    def test_structure_is_set(self):
        if not hasattr(self.model, 'structure'):
            return
        self.login()
        response = self.client.post(self._get_add_url(), self.get_good_data())
        self.assertEqual(response.status_code, 302)
        obj = self.model.objects.last()
        self.assertEqual(obj.structure, self.user.profile.structure)

    def test_structure_is_not_changed(self):
        if not hasattr(self.model, 'structure'):
            return
        self.login()
        structure = StructureFactory()
        self.assertNotEqual(structure, self.user.profile.structure)
        obj = self.modelfactory.create(structure=structure)
        self.client.post(obj.get_update_url(), self.get_good_data())
        self.assertEqual(obj.structure, structure)
