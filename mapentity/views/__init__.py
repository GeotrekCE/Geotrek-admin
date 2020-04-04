from .generic import (
    Convert,
    MapEntityList,
    MapEntityFormat,
    MapEntityMapImage,
    MapEntityDocument,
    MapEntityDocumentBase,
    MapEntityDocumentOdt,
    MapEntityDocumentWeasyprint,
    MapEntityMarkupWeasyprint,
    DocumentConvert,
    MapEntityCreate,
    MapEntityDetail,
    MapEntityUpdate,
    MapEntityDelete,
)
from .api import (
    MapEntityLayer,
    MapEntityJsonList,
    MapEntityViewSet
)
from .mixins import (
    HttpJSONResponse,
    JSONResponseMixin,
    LastModifiedMixin,
    ModelViewMixin,
)
from .base import (
    serve_attachment,
    JSSettings,
    map_screenshot,
    history_delete,
)
from .logentry import LogEntryList


MAPENTITY_GENERIC_VIEWS = [
    MapEntityLayer,
    MapEntityList,
    MapEntityJsonList,
    MapEntityFormat,
    MapEntityMapImage,
    MapEntityDocument,
    MapEntityMarkupWeasyprint,
    MapEntityCreate,
    MapEntityDetail,
    MapEntityUpdate,
    MapEntityDelete,
]

__all__ = [
    'Convert',
    'MapEntityList',
    'MapEntityFormat',
    'MapEntityMapImage',
    'MapEntityDocument',
    'MapEntityDocumentBase',
    'MapEntityDocumentOdt',
    'MapEntityDocumentWeasyprint',
    'MapEntityMarkupWeasyprint',
    'DocumentConvert',
    'MapEntityCreate',
    'MapEntityDetail',
    'MapEntityUpdate',
    'MapEntityDelete',

    'MapEntityLayer',
    'MapEntityJsonList',
    'MapEntityViewSet',

    'HttpJSONResponse',
    'JSONResponseMixin',
    'LastModifiedMixin',
    'ModelViewMixin',
    'MAPENTITY_GENERIC_VIEWS',

    'serve_attachment',
    'JSSettings',
    'map_screenshot',
    'convert',
    'history_delete',

    'LogEntryList',
]
