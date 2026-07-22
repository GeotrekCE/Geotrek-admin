from django.conf import settings
from mapentity.registry import MapEntityOptions


class StatusOptions(MapEntityOptions):
    """
    Overwrite options for Statuses module to redirect to LandEdge objects
    """

    menu = settings.LANDEDGE_MODEL_ENABLED
    layer = False

    def __init__(self, model):
        super().__init__(model)
        self.url_list = "land:landedge_list"
        self.url_add = "land:landedge_add"
        self.icon = "images/landedge.png"
        self.icon_small = "images/landedge-16.png"
        self.icon_big = "images/landedge-96.png"


class PhysicalEdgeOptions(MapEntityOptions):
    menu = False
    layer = True


class LandEdgeOptions(MapEntityOptions):
    menu = False
    layer = True


class CirculationEdgeOptions(MapEntityOptions):
    menu = False
    layer = True


class CompetenceEdgeOptions(MapEntityOptions):
    menu = False
    layer = True


class WorkManagementEdgeOptions(MapEntityOptions):
    menu = False
    layer = True


class SignageManagementEdgeOptions(MapEntityOptions):
    menu = False
    layer = True
