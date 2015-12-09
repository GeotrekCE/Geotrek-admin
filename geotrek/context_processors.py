# -*- encoding: UTF-8 -*-

"""
Template Context Processors for Geotrek
"""

from django.conf import settings
import json
from geojson import Polygon


def forced_layers(request):
    response = []
    for forced_layer in getattr(settings,
                                'FORCED_LAYERS',
                                []):
        if forced_layer[0] in [layer[0] for layer in settings.LEAFLET_CONFIG['TILES']]:
            response.append(
                Polygon([forced_layer[1]],
                        layer=[layer[1] for layer in settings.LEAFLET_CONFIG['TILES'] if layer[0] == forced_layer[0]][0])
            )
    return {'FORCED_LAYERS': response, }
