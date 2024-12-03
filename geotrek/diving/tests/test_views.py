from django.utils.translation import gettext_lazy as _
from mapentity.tests.factories import SuperUserFactory

from geotrek.authent.tests.factories import StructureFactory
from geotrek.common.tests import CommonLiveTest, CommonTest

from ..models import Dive
from .factories import (
    DiveFactory,
    DiveWithLevelsFactory,
    DivingManagerFactory,
    PracticeFactory,
)


class DiveViewsTests(CommonTest):
    model = Dive
    modelfactory = DiveWithLevelsFactory
    userfactory = DivingManagerFactory
    expected_json_geom = {
        'type': 'Point',
        'coordinates': [-1.3630812, -5.9838563],
    }
    extra_column_list = ['depth', 'advice']
    expected_column_list_extra = ['id', 'name', 'depth', 'advice']
    expected_column_formatlist_extra = ['id', 'depth', 'advice']

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name,
            'published': True,
        }

    def get_expected_datatables_attrs(self):
        return {
            'id': self.obj.pk,
            'levels': self.obj.levels_display,
            'name': self.obj.name_display,
            'thumbnail': 'None',
        }

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'structure': StructureFactory.create().pk,
            'name_en': 'test',
            'practice': PracticeFactory.create().pk,
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }


class DiveViewsLiveTests(CommonLiveTest):
    model = Dive
    modelfactory = DiveFactory
    userfactory = SuperUserFactory
