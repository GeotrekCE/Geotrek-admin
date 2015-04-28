# -*- encoding: utf-8 -*-

from django.utils import translation
from django.utils.translation import ugettext as _

# Workaround https://code.djangoproject.com/ticket/22865
from geotrek.common.models import FileType  # NOQA

from mapentity.tests import MapEntityTest

from geotrek.authent.tests import AuthentFixturesTest


class TranslationResetMixin(object):
    def setUp(self):
        translation.deactivate()
        super(TranslationResetMixin, self).setUp()


class CommonTest(AuthentFixturesTest, TranslationResetMixin, MapEntityTest):
    api_prefix = '/api/en/'

    def get_bad_data(self):
        return {'topology': 'doh!'}, _(u'Topology is not valid.')
