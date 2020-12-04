from geotrek.common.tests import CommonTest
from geotrek.outdoor.models import Site
from geotrek.outdoor.factories import SiteFactory, OutdoorManagerFactory
from geotrek.authent.factories import StructureFactory
from django.utils.translation import gettext as _


class SiteViewsTests(CommonTest):
    model = Site
    modelfactory = SiteFactory
    userfactory = OutdoorManagerFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]}

    def get_expected_json_attrs(self):
        return {
            'name': 'Site',
            'description': 'Blah',
        }

    def get_bad_data(self):
        return {
            'geom': 'doh!'
        }, _('Invalid geometry value.')

    def get_good_data(self):
        return {
            'structure': StructureFactory.create().pk,
            'name_en': 'test en',
            'name_fr': 'test fr',
            'geom': '{"type": "Point", "coordinates":[0, 0]}',
        }
