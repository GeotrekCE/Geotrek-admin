from .default import *

#
#  Django Development
#..........................

DEBUG = True
TEMPLATE_DEBUG = True

SOUTH_TESTS_MIGRATE = False  # Tested at settings.tests

#
#  Developper Toolbar
#..........................

INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
)
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

def custom_show_toolbar(request):
    return True  # Always show toolbar

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'INTERCEPT_REDIRECTS': False,
}
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

#
# Use Geotrek preprod tiles (uses default extent)
#................................................

LEAFLET_CONFIG['TILES'] = [
    (gettext_noop('Scan'), 'http://{s}.tile.osm.org/{z}/{x}/{y}.png'),
    (gettext_noop('Ortho'), 'http://{s}.tiles.mapbox.com/v3/openstreetmap.map-4wvf9l0l/{z}/{x}/{y}.jpg'),
]
LEAFLET_CONFIG['SRID'] = 3857

LOGGING['loggers']['geotrek']['level'] = 'DEBUG'
LOGGING['loggers']['']['level'] = 'DEBUG'
