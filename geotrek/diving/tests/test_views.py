from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from geotrek.authent.models import Structure
from geotrek.common.tests import CommonTest
from geotrek.diving.models import Dive
from geotrek.diving.factories import DiveFactory, DivingManagerFactory, PracticeFactory


class DiveViewsTests(CommonTest):
    model = Dive
    modelfactory = DiveFactory
    userfactory = DivingManagerFactory

    def setUp(self):
        translation.deactivate()

        super(DiveViewsTests, self).setUp()

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _(u'Invalid geometry value.')

    def get_good_data(self):
        return {
            'structure': Structure.objects.first().pk,
            'name_fr': u'test',
            'practice': PracticeFactory.create().pk,
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }
