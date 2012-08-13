from caminae.authent.decorators import trekking_manager_required
from caminae.core.views import (MapEntityLayer, MapEntityList, MapEntityJsonList, 
                                MapEntityDetail, MapEntityCreate, MapEntityUpdate, MapEntityDelete)
from .models import Trek
from .filters import TrekFilter
from .forms import TrekForm


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
