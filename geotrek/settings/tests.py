from .default import *

#
#  Django Tests
#..........................

TEST = True

TEST_EXCLUDE = ('django',)

# Just had to put something here...
LEAFLET_CONFIG['TILES_URL'] = [
    ('Terrain', 'http://{s}.tiles.openstreetmap.org/{z}/{x}/{y}.png',),
    ('Ortho', 'http://{s}.tiles.openstreetmap.org/{z}/{x}/{y}.jpg'),
]

LOGGING['handlers']['console']['level'] = 'CRITICAL'

