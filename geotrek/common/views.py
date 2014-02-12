from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.utils import DatabaseError

from mapentity.helpers import api_bbox
from mapentity.views import JSSettings as BaseJSSettings

from geotrek.common.utils import sql_extent
from geotrek import __version__


class FormsetMixin(object):
    context_name = None
    formset_class = None

    def form_valid(self, form):
        context = self.get_context_data()
        formset_form = context[self.context_name]

        if formset_form.is_valid():
            self.object = form.save()
            formset_form.instance = self.object
            formset_form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(FormsetMixin, self).get_context_data(**kwargs)
        if self.request.POST:
            try:
                context[self.context_name] = self.formset_class(self.request.POST, instance=self.object)
            except ValidationError:
                pass
        else:
            context[self.context_name] = self.formset_class(instance=self.object)
        return context


#
# Concrete views
#..............................


class JSSettings(BaseJSSettings):
    """ Override mapentity base settings in order to provide
    Geotrek necessary stuff.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(JSSettings, self).dispatch(*args, **kwargs)

    def get_context_data(self):
        dictsettings = super(JSSettings, self).get_context_data()
        # Add geotrek map styles
        base_styles = dictsettings['map']['styles']
        for name, override in settings.MAP_STYLES.items():
            merged = base_styles.get(name, {})
            merged.update(override)
            base_styles[name] = merged
        # Add extra stuff (edition, labelling)
        dictsettings['map'].update(
            snap_distance=settings.SNAP_DISTANCE,
            colorspool=settings.LAND_COLORS_POOL,
        )
        dictsettings['version'] = __version__
        dictsettings.setdefault('urls', {})
        dictsettings['urls']['path_graph'] = reverse('core:path_json_graph')
        return dictsettings


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_check_extents(request):
    """
    This view allows administrators to visualize data and configured extents.

    Since it's the first, we implemented this in a very rough way. If there is
    to be more admin tools like this one. Move this to a separate Django app and
    style HTML properly.
    """
    path_extent_native = sql_extent("SELECT ST_Extent(geom) FROM l_t_troncon;")
    path_extent = api_bbox(path_extent_native)
    try:
        dem_extent_native = sql_extent("SELECT ST_Extent(rast::geometry) FROM mnt;")
        dem_extent = api_bbox(dem_extent_native)
    except DatabaseError:  # mnt table missing
        dem_extent_native = None
        dem_extent = None
    tiles_extent_native = settings.SPATIAL_EXTENT
    tiles_extent = api_bbox(tiles_extent_native)
    viewport_native = settings.LEAFLET_CONFIG['SPATIAL_EXTENT']
    viewport = api_bbox(viewport_native, srid=settings.API_SRID)

    leafletbounds = lambda bbox: [[bbox[1], bbox[0]], [bbox[3], bbox[2]]]

    context = dict(
        path_extent=leafletbounds(path_extent),
        path_extent_native=path_extent_native,
        dem_extent=leafletbounds(dem_extent) if dem_extent else None,
        dem_extent_native=dem_extent_native,
        tiles_extent=leafletbounds(tiles_extent),
        tiles_extent_native=tiles_extent_native,
        viewport=leafletbounds(viewport),
        viewport_native=viewport_native,
        SRID=settings.SRID,
        API_SRID=settings.API_SRID,
    )
    return render(request, 'common/check_extents.html', context)
