"""

    Geotrek startup script.

    This is executed only once at startup.

"""
from south.signals import post_migrate
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from mapentity.helpers import api_bbox

from geotrek.common.utils.postgresql import load_sql_files


"""
    http://djangosnippets.org/snippets/2311/
    Ensure South will update our custom SQL during a call to `migrate`.
"""

def run_initial_sql(sender, **kwargs):
    app_label = kwargs.get('app')
    load_sql_files(app_label)


post_migrate.connect(run_initial_sql, dispatch_uid="geotrek.core.sqlautoload")


"""
    TODO: keep until django-leaflet is upgraded to 0.8
"""
if settings.LEAFLET_CONFIG['SRID'] != 3857:
    # Due to bug in Leaflet/Proj4Leaflet ()
    # landscape extents are not supported.
    extent = settings.SPATIAL_EXTENT
    is_landscape = extent[2] - extent[0] > extent[3] - extent[1]
    if is_landscape:
        raise ImproperlyConfigured('Landscape spatial_extent not supported (%s).' % (extent,))

"""
    Computed client-side setting.
"""
settings.LEAFLET_CONFIG['SPATIAL_EXTENT'] = api_bbox(settings.SPATIAL_EXTENT, buffer=0.5)
