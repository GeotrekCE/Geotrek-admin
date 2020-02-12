from rest_framework.renderers import JSONRenderer


class GeoJSONRenderer(JSONRenderer):
    format = 'geojson'
