from caminae.mapentity.tests import MapEntityTest
from caminae.authent.factories import TrekkingManagerFactory

from caminae.core.factories import PathFactory
from caminae.trekking.models import POI, Trek
from caminae.trekking.factories import (POIFactory, POITypeFactory, TrekFactory,
    TrekNetworkFactory, UsageFactory, WebLinkFactory)


class POIViewsTest(MapEntityTest):
    model = POI
    modelfactory = POIFactory
    userfactory = TrekkingManagerFactory

    def get_bad_data(self):
        baddata, msg = super(POIViewsTest, self).get_bad_data()
        return baddata, u'Acune valeur g\xe9om\xe9trique fournie.'   # TODO until points managed as topologies

    def get_good_data(self):
        return {
            'name_fr': 'test',
            'name_en': 'test',
            'name_it': 'testo',
            'description_fr': 'ici',
            'description_en': 'here',
            'description_it': 'aca',
            'type': POITypeFactory.create().pk,
            'geom': 'POINT (0.0 0.0 0.0)',
        }


class TrekViewsTest(MapEntityTest):
    model = Trek
    modelfactory = TrekFactory
    userfactory = TrekkingManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'name_fr': '',
            'name_it': '',
            'name_en': '',
            'departure_fr': '',
            'departure_it': '',
            'departure_en': '',
            'arrival_fr': '',
            'arrival_en': '',
            'arrival_it': '',
            'validated': '',
            'difficulty': '',
            'route': '',
            'destination': '',
            'description_teaser_fr': '',
            'description_teaser_it': '',
            'description_teaser_en': '',
            'description_fr': '',
            'description_it': '',
            'description_en': '',
            'ambiance_fr': '',
            'ambiance_it': '',
            'ambiance_en': '',
            'disabled_infrastructure_fr': '',
            'disabled_infrastructure_it': '',
            'disabled_infrastructure_en': '',
            'duration': '0',
            'is_park_centered': '',
            'is_transborder': '',
            'advised_parking': 'Very close',
            'parking_location': 'POINT (1.0 1.0 0.0)',
            'public_transport': 'huhu',
            'advice_fr': '',
            'advice_it': '',
            'advice_en': '',
            'networks': TrekNetworkFactory.create().pk,
            'usages': UsageFactory.create().pk,
            'web_links': WebLinkFactory.create().pk,
            'geom': '{"paths": [%s]}' % path.pk,
        }
