from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from geotrek.common.tests import CommonTest
from geotrek.tourism.models import TouristicContent, TouristicEvent
from geotrek.tourism.factories import (TouristicContentFactory,
                                       TouristicContentCategoryFactory,
                                       TouristicEventFactory)
from mapentity.factories import SuperUserFactory


class TouristicContentViewsTests(CommonTest):
    model = TouristicContent
    modelfactory = TouristicContentFactory
    userfactory = SuperUserFactory

    def setUp(self):
        translation.deactivate()
        super(TouristicContentViewsTests, self).setUp()

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'name_fr': 'test',
            'category': TouristicContentCategoryFactory.create().pk,
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }


class TouristicEventViewsTests(CommonTest):
    model = TouristicEvent
    modelfactory = TouristicEventFactory
    userfactory = SuperUserFactory

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'name_fr': 'test',
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }
