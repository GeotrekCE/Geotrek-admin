from django.conf import settings as settings_ # import the settings file


def settings(context):
    return dict(
        TITLE=settings_.TITLE,
        DEBUG=settings_.DEBUG,
        DATE_INPUT_FORMAT_JS=settings_.DATE_INPUT_FORMATS[0].replace('%Y', 'yyyy').replace('%m', 'mm').replace('%d', 'dd'),
        
        LAYERCOLOR_PATHS=settings_.LAYERCOLOR_PATHS,
        LAYERCOLOR_LAND=settings_.LAYERCOLOR_LAND,
        LAYERCOLOR_OTHERS=settings_.LAYERCOLOR_OTHERS,
    )
