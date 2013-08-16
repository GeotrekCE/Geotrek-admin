from .default import *

#
#  Django Development
#..........................

DEBUG = True
TEMPLATE_DEBUG = True

#
#  Developper Toolbar
#..........................

INSTALLED_APPS += (
    'debug_toolbar',
    'concurrent_server',
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
#  Convertit server
#...........................

CONVERSION_SERVER = 'http://0.0.0.0:6543'


#
# Private MakinaCorpus IGN Lambert tiles
#........................................

LEAFLET_CONFIG['TILES_URL'] = [
    ('Terrain', 'http://geobi.makina-corpus.net/ecrins-sentiers-tiles/ign/{z}/{x}/{y}.png',),
    ('Ortho', 'http://geobi.makina-corpus.net/ecrins-sentiers-tiles/ortho/{z}/{x}/{y}.jpg'),
]

LOGGING['loggers']['geotrek']['level'] = 'DEBUG'
LOGGING['loggers']['']['level'] = 'DEBUG'
