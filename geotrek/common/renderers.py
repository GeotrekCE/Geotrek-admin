from rest_framework.renderers import JSONRenderer


class GTAMRenderer(JSONRenderer):
    format = "gtam"
    media_type = "application/json"
