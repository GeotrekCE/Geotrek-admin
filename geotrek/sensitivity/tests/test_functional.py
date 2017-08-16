from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from geotrek.common.tests import CommonTest
from geotrek.authent.models import default_structure
from geotrek.sensitivity.models import SensitiveArea
from geotrek.sensitivity.factories import SensitiveAreaFactory, SpeciesFactory
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
        }, _(u'Invalid geometry value.')

    def get_good_data(self):
        return {
            'species': SpeciesFactory.create().pk,
            'structure': default_structure().pk,
            'geom': '{"type": "Polygon", "coordinates":[[[0, 0], [0, 1], [1, 0], [0, 0]]]}',
        }
