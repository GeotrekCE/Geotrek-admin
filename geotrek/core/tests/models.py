from django.db import models

from geotrek.core.models import Topology


class PointTopologyTestModel(Topology):
    topo_object = models.OneToOneField(
        Topology, parent_link=True, on_delete=models.CASCADE
    )
    geometry_types_allowed = ["POINT"]
