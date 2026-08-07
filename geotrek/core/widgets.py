"""
Widgets de topologie indépendants avec leur propre logique de rendu.
Basés sur BaseGeometryWidget, complètement séparés de MapWidget.
"""

from django.contrib.gis.forms.widgets import BaseGeometryWidget
from django.core import validators
from django.forms import Media
from django.template.defaultfilters import slugify
from mapentity.widgets import MapWidget

from .models import Topology


class BaseTopologyWidget(BaseGeometryWidget):
    template_name = "core/line_topology_widget.html"
    display_raw = False
    modifiable = True
    is_line_topology = False
    is_point_topology = False

    def serialize(self, value):
        return value.serialize() if hasattr(value, "serialize") else ""

    def deserialize(self, value):
        if isinstance(value, int):
            return Topology.objects.get(pk=value)
        try:
            return Topology.deserialize(value)
        except ValueError:
            return None

    def _get_topology_attrs(self, name, attrs=None):
        attrs = attrs or {}

        # Génération des IDs pour les éléments HTML et JavaScript
        map_id_css = slugify(attrs.get("id", name))
        map_id = map_id_css.replace("-", "_")

        attrs.update(
            {
                "id": map_id,
                "id_css": map_id_css,
                "id_map": map_id_css + "_map",
                "modifiable": self.modifiable,
                "is_line_topology": self.is_line_topology,
                "is_point_topology": self.is_point_topology,
                "target_map": attrs.get(
                    "target_map", getattr(self, "target_map", None)
                ),
            }
        )
        return attrs

    def get_context(self, name, value, attrs):
        # Gestion des valeurs vides
        value = None if value in validators.EMPTY_VALUES else value

        # Récupération du contexte parent
        context = super().get_context(name, value, attrs)

        # Ajout des attributs spécifiques à la topologie
        topology_attrs = self._get_topology_attrs(name, attrs)
        context.update(topology_attrs)

        # Ajout de la valeur sérialisée pour le template
        context["serialized"] = self.serialize(value)

        return context

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, int):
            try:
                value = Topology.objects.get(pk=value)
            except Topology.DoesNotExist:
                value = None

        # Mise à jour des attributs avec les flags de topologie
        attrs = attrs or {}
        attrs.update(
            {
                "is_line_topology": self.is_line_topology,
                "is_point_topology": self.is_point_topology,
            }
        )

        return super().render(name, value, attrs, renderer)


class LineTopologyWidget(BaseTopologyWidget):
    is_line_topology = True


class PointLineTopologyWidget(BaseTopologyWidget):
    is_line_topology = True
    is_point_topology = True


class GeotrekMapWidget(MapWidget):
    """
    MapWidget with features specific to Geotrek:
      - Set geom_changed to True when geom is modified.
    """

    def __init__(self, attrs=None, *args, **kwargs):
        attrs = attrs or {}
        self.modifiable = attrs.pop("modifiable", True)
        super().__init__(attrs=attrs, *args, **kwargs)

    @property
    def media(self):
        media = super().media
        return media + Media(js=["core/mapwidget_set_geom_changed.js"])
