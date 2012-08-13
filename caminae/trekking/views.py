from caminae.authent.decorators import trekking_manager_required
from caminae.mapentity.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, 
                                MapEntityDetail, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from .models import Trek, POI
from .filters import TrekFilter, POIFilter
from .forms import TrekForm, POIForm


class TrekLayer(MapEntityLayer):
    model = Trek


class TrekList(MapEntityList):
    model = Trek
    filterform = TrekFilter
    columns = ['name', 'departure', 'arrival']


class TrekJsonList(MapEntityJsonList, TrekList):
    pass


class TrekDetail(MapEntityDetail):
    model = Trek

    def can_edit(self):
        return self.request.user.profile.is_trekking_manager()


class TrekCreate(MapEntityCreate):
    model = Trek
    form_class = TrekForm

    @trekking_manager_required('trekking:trek_list')
    def dispatch(self, *args, **kwargs):
        return super(TrekCreate, self).dispatch(*args, **kwargs)


class TrekUpdate(MapEntityUpdate):
    model = Trek
    form_class = TrekForm

    @trekking_manager_required('trekking:trek_detail')
    def dispatch(self, *args, **kwargs):
        return super(TrekUpdate, self).dispatch(*args, **kwargs)


class TrekDelete(MapEntityDelete):
    model = Trek

    @trekking_manager_required('trekking:trek_detail')
    def dispatch(self, *args, **kwargs):
        return super(TrekDelete, self).dispatch(*args, **kwargs)


class POILayer(MapEntityLayer):
    model = POI


class POIList(MapEntityList):
    model = POI
    filterform = POIFilter
    columns = ['name', 'type']


class POIJsonList(MapEntityJsonList, POIList):
    pass


class POIDetail(MapEntityDetail):
    model = POI

    def can_edit(self):
        return self.request.user.profile.is_trekking_manager()


class POICreate(MapEntityCreate):
    model = POI
    form_class = POIForm

    @trekking_manager_required('trekking:poi_list')
    def dispatch(self, *args, **kwargs):
        return super(TrekCreate, self).dispatch(*args, **kwargs)


class POIUpdate(MapEntityUpdate):
    model = POI
    form_class = POIForm

    @trekking_manager_required('trekking:poi_detail')
    def dispatch(self, *args, **kwargs):
        return super(POIUpdate, self).dispatch(*args, **kwargs)


class POIDelete(MapEntityDelete):
    model = POI

    @trekking_manager_required('trekking:poi_detail')
    def dispatch(self, *args, **kwargs):
        return super(POIDelete, self).dispatch(*args, **kwargs)
