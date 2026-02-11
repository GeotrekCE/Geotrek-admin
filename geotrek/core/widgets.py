"""
Widgets de topologie indépendants avec leur propre logique de rendu.
Basés sur BaseGeometryWidget, complètement séparés de MapWidget.
"""

import json

from django.contrib.gis.forms.widgets import BaseGeometryWidget
from django.core import validators
from django.template.defaultfilters import slugify

from .models import Topology


class BaseTopologyWidget(BaseGeometryWidget):
    """
    Widget de base pour les topologies, complètement indépendant de MapWidget.
    Utilise uniquement le template topology_widget_fragment.html.
    """

    template_name = "core/topology_widget_fragment.html"
    display_raw = False
    modifiable = True
    is_line_topology = False
    is_point_topology = False

    def serialize(self, value):
        """Sérialise une topologie en JSON."""
        return value.serialize() if hasattr(value, "serialize") else ""

    def deserialize(self, value):
        """Désérialise une valeur en objet Topology."""
        if isinstance(value, int):
            return Topology.objects.get(pk=value)
        try:
            return Topology.deserialize(value)
        except ValueError:
            return None

    def _get_topology_attrs(self, name, attrs=None):
        """
        Prépare les attributs nécessaires pour le rendu du template de topologie.
        Reprend la logique de MapWidget mais pour les topologies.
        """
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
        """
        Prépare le contexte pour le rendu du template topology_widget_fragment.html.
        """
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
        """
        Rendu du widget de topologie.
        Gère la conversion des valeurs entières en objets Topology.
        """
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


class PointTopologyWidget(BaseTopologyWidget):
    is_point_topology = True


class PointLineTopologyWidget(BaseTopologyWidget):
    is_line_topology = True
    is_point_topology = True


# Garder SnappedLineStringWidget tel quel - pas de modification
class SnappedLineStringWidget(BaseTopologyWidget):
    # geometry_field_class = "MapEntity.GeometryField.GeometryFieldSnap"

    def serialize(self, value):
        geojson = super().serialize(value)
        snaplist = []
        if value:
            snaplist = [None for c in range(len(value.coords))]
        value = {"geom": geojson, "snap": snaplist}
        return json.dumps(value)

    def deserialize(self, value):
        if isinstance(value, str) and value:
            value = json.loads(value)
            value = value["geom"]
        return super().deserialize(value)
