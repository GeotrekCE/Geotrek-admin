import io
import json
import os
import re
import textwrap
import zipfile
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import PurePath
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, LineString, Point
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from modeltranslation.utils import build_localized_fieldname
from paperclip.models import attachment_upload, random_suffix_regexp

from geotrek.common.models import Attachment, Label, License, Theme
from geotrek.common.parsers import (
    ApidaeBaseParser,
    AttachmentParserMixin,
    DownloadImportError,
    GeotrekParser,
    GlobalImportError,
    OpenStreetMapAttachmentsParserMixin,
    OpenStreetMapParser,
    OpenStreetMapAttachmentsParserMixin,
    Parser,
    RowImportError,
    ShapeParser,
    ValueImportError,
)
from geotrek.common.utils.parsers import (
    GeomValueError,
    get_geom_from_gpx,
    get_geom_from_kml,
)
from geotrek.core.models import Path, Topology
from geotrek.trekking.models import (
    POI,
    Accessibility,
    DifficultyLevel,
    OrderedTrekChild,
    Service,
    Trek,
    TrekNetwork,
)


class DurationParserMixin:
    def filter_duration(self, src, val):
        val = val.upper().replace(",", ".")
        try:
            if "H" in val:
                hours, minutes = val.split("H", 2)
                hours = float(hours.strip())
                minutes = float(minutes.strip()) if minutes.strip() else 0
                if hours < 0 or minutes < 0 or minutes >= 60:
                    raise ValueError
                return hours + minutes / 60
            else:
                hours = float(val.strip())
                if hours < 0:
                    raise ValueError
                return hours
        except (TypeError, ValueError):
            self.add_warning(
                _(
                    "Bad value '%(val)s' for field %(src)s. Should be like '2h30', '2,5' or '2.5'"
                )
                % {"val": val, "src": src}
            )
            return None


class POIParser(AttachmentParserMixin, ShapeParser):
    label = "Import POI"
    label_fr = "Import POI"
    label_en = "Import POI"
    model = POI
    simplify_tolerance = 2
    eid = "name"
    constant_fields = {
        "published": True,
        "deleted": False,
    }
    natural_keys = {
        "type": "label",
    }
    field_options = {"geom": {"required": True}, "type": {"required": True}}
    topology = Topology.objects.none()

    def start(self):
        super().start()
        if settings.TREKKING_TOPOLOGY_ENABLED and not Path.objects.exists():
            raise GlobalImportError(
                _("You need to add a network of paths before importing POIs")
            )

    def filter_geom(self, src, val):
        self.topology = Topology.objects.none()
        if val is None:
            # We use RowImportError because with TREKKING_TOPOLOGY_ENABLED, geom has default value POINT(0 0)
            raise RowImportError(_("Invalid geometry"))
        if val.geom_type != "Point":
            raise RowImportError(
                _(
                    "Invalid geometry type for field '{src}'. Should be Point, not {geom_type}"
                ).format(src=src, geom_type=val.geom_type)
            )
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Use existing topology helpers to transform a Point(x, y)
            # to a path aggregation (topology)
            geometry = val.transform(settings.API_SRID, clone=True)
            geometry.coord_dim = 2
            serialized = f'{{"lng": {geometry.x}, "lat": {geometry.y}}}'
            self.topology = Topology.deserialize(serialized)
            # Move deserialization aggregations to the POI
        return val

    def parse_obj(self, row, operation):
        super().parse_obj(row, operation)
        if settings.TREKKING_TOPOLOGY_ENABLED and self.obj.geom and self.topology:
            self.obj.mutate(self.topology)


class TrekParser(DurationParserMixin, AttachmentParserMixin, ShapeParser):
    label = "Import trek"
    label_fr = "Import itinéraires"
    label_en = "Import trek"
    model = Trek
    simplify_tolerance = 2
    eid = "name"
    constant_fields = {
        "published": True,
        "deleted": False,
    }
    natural_keys = {
        "difficulty": "difficulty",
        "route": "route",
        "themes": "label",
        "practice": "name",
        "accessibilities": "name",
        "networks": "network",
    }

    def filter_geom(self, src, val):
        if val is None:
            return None
        if val.geom_type == "MultiLineString":
            points = val[0]
            for i, path in enumerate(val[1:]):
                distance = Point(points[-1]).distance(Point(path[0]))
                if distance > 5:
                    self.add_warning(
                        _(
                            "Not contiguous segment {i} ({distance} m) for geometry for field '{src}'"
                        ).format(
                            i=i + 2,
                            p1=points[-1],
                            p2=path[0],
                            distance=int(distance),
                            src=src,
                        )
                    )
                points += path
            return points
        elif val.geom_type != "LineString":
            # We use RowImportError because geom has default value POINT(0 0)
            raise RowImportError(
                _(
                    "Invalid geometry type for field '{src}'. Should be LineString, not {geom_type}"
                ).format(src=src, geom_type=val.geom_type)
            )
        return val


class GeotrekTrekParser(GeotrekParser):
    """Geotrek parser for Trek"""

    fill_empty_translated_fields = True
    url = None
    model = Trek
    constant_fields = {
        "deleted": False,
    }
    replace_fields = {"eid": "uuid", "eid2": "second_external_id", "geom": "geometry"}
    url_categories = {
        "structure": "structure",
        "difficulty": "trek_difficulty",
        "route": "trek_route",
        "themes": "theme",
        "practice": "trek_practice",
        "accessibilities": "trek_accessibility",
        "networks": "trek_network",
        "labels": "label",
        "source": "source",
    }
    categories_keys_api_v2 = {
        "structure": "name",
        "difficulty": "label",
        "route": "route",
        "themes": "label",
        "practice": "name",
        "accessibilities": "name",
        "networks": "label",
        "labels": "name",
        "source": "name",
    }
    natural_keys = {
        "structure": "name",
        "difficulty": "difficulty",
        "route": "route",
        "themes": "label",
        "practice": "name",
        "accessibilities": "name",
        "networks": "network",
        "labels": "name",
        "source": "name",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/trek"

    def filter_parking_location(self, src, val):
        if val:
            return Point(val[0], val[1], srid=settings.API_SRID)

    def filter_points_reference(self, src, val):
        if val:
            geom = GEOSGeometry(json.dumps(val))
            return geom.transform(settings.SRID, clone=True)

    def fetch_missing_categories_for_tour_steps(self, step):
        # For all categories, search missing values in mapping
        for category, route in self.url_categories.items():
            category_mapping = self.field_options.get(category, {}).get("mapping", {})
            category_values = step.get(category)
            if not isinstance(category_values, list):
                category_values = [category_values]
            for value in category_values:
                # If category PK is not found in mapping, fetch it from provider
                if value is not None and value not in list(category_mapping.keys()):
                    if self.categories_keys_api_v2.get(category):
                        try:
                            result = self.request_or_retry(
                                f"{self.url}/api/v2/{route}/{int(value)}"
                            ).json()
                        except DownloadImportError:
                            self.add_warning(
                                f"Could not download {category} with id {value} from {self.provider}"
                                f" for Tour step {step.get('uuid')}"
                            )
                            continue
                        # Update mapping like we usually do
                        label = result[self.categories_keys_api_v2[category]]
                        if isinstance(
                            result[self.categories_keys_api_v2[category]], dict
                        ):
                            if label[settings.MODELTRANSLATION_DEFAULT_LANGUAGE]:
                                self.field_options[category]["mapping"][value] = (
                                    self.replace_mapping(
                                        label[
                                            settings.MODELTRANSLATION_DEFAULT_LANGUAGE
                                        ],
                                        route,
                                    )
                                )
                        else:
                            if label:
                                self.field_options[category]["mapping"][value] = (
                                    self.replace_mapping(label, category)
                                )

    def end(self):
        """Add children after all treks imported are created in database."""
        self.next_url = f"{self.url}/api/v2/tour"
        portals = self.portals_filter
        try:
            params = {
                "in_bbox": ",".join([str(coord) for coord in self.bbox.extent]),
                "fields": "steps,id,uuid,published",
                "portals": ",".join(portals) if portals else "",
            }
            response = self.request_or_retry(f"{self.next_url}", params=params)
            results = response.json()["results"]
            steps_to_download = 0
            final_children = {}
            for result in results:
                final_children[result["uuid"]] = []
                for step in result["steps"]:
                    final_children[result["uuid"]].append(step["id"])
                    if not any(step["published"].values()):
                        steps_to_download += 1
            self.nb = steps_to_download

            for key, value in final_children.items():
                if value:
                    trek_parent_instance = Trek.objects.filter(eid=key)
                    if not trek_parent_instance:
                        self.add_warning(
                            _(
                                "Trying to retrieve children for missing trek : could not find trek with UUID %(key)s"
                            )
                            % {"key": key}
                        )
                        continue
                    order = 0
                    for child_id in value:
                        response = self.request_or_retry(
                            f"{self.url}/api/v2/trek/{child_id}"
                        )
                        child_trek = response.json()
                        # The Tour step might be linked to categories that are not published,
                        # we have to retrieve the missing ones first
                        self.fetch_missing_categories_for_tour_steps(child_trek)
                        self.parse_row(child_trek)
                        trek_child_instance = self.obj
                        OrderedTrekChild.objects.update_or_create(
                            parent=trek_parent_instance[0],
                            child=trek_child_instance,
                            defaults={"order": order},
                        )
                        order += 1
        except Exception as e:
            self.add_warning(
                _("An error occurred in children generation: %(message)s")
                % {"message": getattr(e, "message", repr(e))}
            )
        super().end()


class GeotrekServiceParser(GeotrekParser):
    """Geotrek parser for Service"""

    fill_empty_translated_fields = True
    url = None
    model = Service
    constant_fields = {
        "deleted": False,
    }
    replace_fields = {"eid": "uuid", "geom": "geometry"}
    url_categories = {
        "structure": "structure",
        "type": "service_type",
    }
    categories_keys_api_v2 = {
        "structure": "name",
        "type": "name",
    }
    natural_keys = {"structure": "name", "type": "name"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/service"


class GeotrekPOIParser(GeotrekParser):
    """Geotrek parser for GeotrekPOI"""

    fill_empty_translated_fields = True
    url = None
    model = POI
    constant_fields = {
        "deleted": False,
    }
    replace_fields = {"eid": "uuid", "geom": "geometry"}
    url_categories = {
        "structure": "structure",
        "type": "poi_type",
    }
    categories_keys_api_v2 = {
        "structure": "name",
        "type": "label",
    }
    natural_keys = {
        "structure": "name",
        "type": "label",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/poi"


class ApidaeTranslatedField:
    apidae_prefix = "libelle"

    def __init__(self, separator=""):
        self._separator = separator
        self._translated_items = defaultdict(list)

    def append(self, translated_value, transform_func=None):
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            translation_value = translated_value.get(
                f"{ApidaeTranslatedField.apidae_prefix}{lang.capitalize()}", ""
            )
            if transform_func:
                translation_value = transform_func(translation_value)
            self._translated_items[lang].append(translation_value)

    def to_dict(self):
        rv = {}
        for key, value in self._translated_items.items():
            rv[key] = self._separator.join(value)
        return rv


class ApidaeBaseTrekkingParser(ApidaeBaseParser):
    """Add the `expand_translations` field option.
    Map an APIDAE translated field as src to a Geotrek translated field as dst in the parser's `fields` attribute. Set
    the `expand_translations` option to True on that field for the corresponding mapping to be expanded into a mapping
    of all translation sub-fields for all configured languages.

    For instance:

    fields = {
        'name': 'nom',
    }

    turns into

    fields = {
        'name_fr': 'nom.libelleFr',
        'name_en': 'nom.libelleEn',
        'name_es': 'nom.libelleEs',
        'name_it': 'nom.libelleIt',
    }
    """

    apidae_translation_prefix = "libelle"

    def __init__(self, *args, **kwargs):
        self._expand_fields_mapping_with_translation_fields()
        super().__init__(*args, **kwargs)

    def _expand_fields_mapping_with_translation_fields(self):
        self.fields = self.fields.copy()
        translated_fields_to_expand = [
            field
            for field, options in self.field_options.items()
            if options.get("expand_translations") is True
        ]
        for translated_field in translated_fields_to_expand:
            src = self.fields[translated_field]
            del self.fields[translated_field]
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                self.fields[build_localized_fieldname(translated_field, lang)] = (
                    f"{src}.{self.apidae_translation_prefix}{lang.capitalize()}"
                )

    @classmethod
    def _get_default_translation_src(cls):
        return (
            cls.apidae_translation_prefix
            + settings.MODELTRANSLATION_DEFAULT_LANGUAGE.capitalize()
        )


def _prepare_attachment_from_apidae_illustration(illustration, translation_src):
    def get_translation_value_of(key):
        translated_field = illustration.get(key)
        if not translated_field:
            return ""
        return translated_field.get(translation_src, "")

    legende = get_translation_value_of("legende")
    copyright = get_translation_value_of("copyright")
    title = get_translation_value_of("nom")
    return (
        illustration["traductionFichiers"][0]["url"],
        legende or title,
        copyright,
        title,
    )


class ApidaeTrekParser(AttachmentParserMixin, ApidaeBaseTrekkingParser):
    model = Trek
    eid = "eid"
    separator = None

    # Parameters to build the request
    url = "https://api.apidae-tourisme.com/api/v002/recherche/list-objets-touristiques/"
    api_key = None
    project_id = None
    selection_id = None
    size = 20
    skip = 0
    responseFields = [
        "id",
        "nom",
        "multimedias",
        "gestion",
        "presentation",
        "localisation",
        "liens",
        "prestations",
        "ouverture",
        "descriptionTarif",
        "informationsEquipement",
        "illustrations",
        "informations",
    ]
    locales = ["fr", "en"]

    # Fields mapping
    fill_empty_translated_fields = True
    fields = {
        "name": "nom",
        "description_teaser": "presentation.descriptifCourt",
        "ambiance": "presentation.descriptifDetaille",
        "description": (
            "ouverture",
            "presentation.descriptifsThematises.*",
            "informationsEquipement.itineraire",
            "descriptionTarif",
            "informations.moyensCommunication",
        ),
        "geom": "multimedias",
        "eid": "id",
        "advised_parking": "localisation.adresse.adresse1",
        "departure": "localisation.adresse.commune.nom",
        "access": "localisation.geolocalisation.complement",
        "difficulty": "prestations.typesClientele",
        "practice": "informationsEquipement.activites",
        "duration": (
            "informationsEquipement.itineraire.dureeJournaliere",
            "informationsEquipement.itineraire.dureeItinerance",
        ),
        "advice": "informationsEquipement.itineraire.passagesDelicats",
        "route": "informationsEquipement.itineraire.itineraireType",
        "accessibility_covering": "informationsEquipement.itineraire.naturesTerrain.*",
        "gear": (
            "informationsEquipement.itineraire.referencesCartographiques",
            "informationsEquipement.itineraire.referencesTopoguides",
        ),
        "structure": "gestion.membreProprietaire.nom",
    }
    m2m_fields = {
        "source": "gestion.membreProprietaire",
        "themes": "presentation.typologiesPromoSitra.*",
        "labels": [
            "presentation.typologiesPromoSitra.*",
            "localisation.environnements.*",
        ],
        "networks": "informationsEquipement.activites",
        "accessibilities": "informationsEquipement.itineraire.naturesTerrain.*",
    }
    natural_keys = {
        "source": "name",
        "themes": "label",
        "labels": "name",
        "difficulty": "difficulty",
        "practice": "name",
        "networks": "network",
        "route": "route",
        "accessibilities": "name",
        "structure": "name",
    }
    field_options = {
        "source": {"create": True},
        "themes": {"create": True},
        "labels": {"create": True},
        "name": {"expand_translations": True},
        "description_teaser": {"expand_translations": True},
        "ambiance": {"expand_translations": True},
        "access": {"expand_translations": True},
        "difficulty": {"create": True},
        "related_treks": {"create": True},
        "practice": {"create": True},
        "networks": {"create": True},
        "advice": {"expand_translations": True},
        "route": {
            # Relevant default mapping considering routes in trekking data fixture.
            "mapping": {
                "BOUCLE": "Boucle",
                "ALLER_RETOUR": "Aller-retour",
                "ALLER_ITINERANCE": "Traversée",
            }
        },
        "accessibilities": {"create": True},
        "geom": {"required": True},
        "structure": {"create": True},
    }
    non_fields = {
        "attachments": "illustrations",
        "trek_children": "liens.liensObjetsTouristiquesTypes.*",
    }

    # Relevant default mapping considering practices in trekking data fixture.
    # The practice key must be the name in the default language on your instance.
    practices_mapped_with_activities_ids = {
        "Pédestre": [
            3333,  # Itinéraire de randonnée pédestre
            3331,  # Parcours / sentier thématique
            5324,  # Parcours de marche nordique
        ],
        "Vélo": [
            3283,  # Itinéraire cyclotourisme
            5447,  # Itinéraire de Vélo à Assistance Electrique
            3280,  # Véloroute et voie verte
        ],
        "VTT": [
            3284,  # Itinéraire VTT
            3281,  # Piste de descente VTT
            5446,  # Itinéraire enduro
            4174,  # Itinéraire Fat Bike
            6168,  # Itinéraire fauteuil tout terrain
            6224,  # Itinéraire gravel bike
        ],
        "Cheval": [
            3313,  # Itinéraire de randonnée équestre
        ],
        "Trail": [
            4201,  # Itinéraire de Trail
        ],
        "VTTAE": [
            6225,  # Itinéraire de VTT à Assistance Électrique
        ],
    }
    practices_mapped_with_default_activities_ids = {
        "Pédestre": 3184,  # Sports pédestres
        "Vélo": 3113,  # Sports cyclistes
        "Cheval": 3165,  # Sports équestres
    }
    natures_de_terrain_ids_as_accessibilities = [
        4244,  # Adapté aux poussettes de ville
        4245,  # Adapté aux poussettes tout terrain
    ]
    typologies_sitra_ids_as_labels = [
        1599,  # Déconseillé par mauvais temps
        1676,  # En plein air
        4639,  # Conseillé par forte chaleur
        4819,  # Paysages
        5022,  # Respirando
        4971,  # Inscrit au PDIPR
        3845,  # Itinéraire France vélo
        6566,  # Label Espace Cyclosport
        6049,  # Label Vélo et Fromages
        1582,  # Label VTT - FFC
        5538,  # Label VTT - FFCT
        6825,  # Station de Trail®
        6608,  # Site sur-fréquenté
        1602,  # Circuits de France
    ]
    typologies_sitra_ids_as_themes = [
        6155,  # Adrénaline
        6156,  # Au fil de l'eau
        6368,  # Familial
        6153,  # Faune
        6154,  # Flore
        6157,  # Géologie
        6163,  # Gourmande
        6158,  # Historique
        6679,  # Itinéraire d'accès à un refuge
        6159,  # Vue exceptionnelle
        6160,  # Pastoralisme
        6161,  # Volcanisme
    ]
    environnements_ids_as_labels = [
        135,  # A la campagne
        4630,  # Dans une réserve naturelle
        171,  # En montagne
        189,  # En moyenne montagne
        186,  # En haute montagne
        6238,  # Présence de troupeaux et chiens de protection
        3743,  # Au bord de l'eau
        147,  # Lac ou plan d'eau à moins de 300 m
        149,  # Rivière ou fleuve à moins de 300 m
        156,  # Etang à moins de 300 m
        153,  # En forêt
        187,  # Isolé
        195,  # Village à -2 km
        6464,  # Vue cascade
        4006,  # Vue sur fleuve ou rivière
        169,  # Vue montagne
        3978,  # Vue sur le vignoble
        6087,  # Vue panoramique
    ]
    activites_ids_as_networks = [
        3333,  # Itinéraire de randonnée pédestre
        3331,  # Parcours / sentier thématique
        5324,  # Parcours de marche nordique
        3283,  # Itinéraire cyclotourisme
        5447,  # Itinéraire de Vélo à Assistance Electrique
        3280,  # Véloroute et voie verte
        3284,  # Itinéraire VTT
        3281,  # Piste de descente VTT
        5446,  # Itinéraire enduro
        4174,  # Itinéraire Fat Bike
        6168,  # Itinéraire fauteuil tout terrain
        6224,  # Itinéraire gravel bike
        3313,  # Itinéraire de randonnée équestre
        4201,  # Itinéraire de Trail
        6225,  # Itinéraire de VTT à Assistance Électrique
    ]
    types_clientele_ids_as_difficulty_levels = [
        587,  # Niveau vert - Très facile
        588,  # Niveau bleu - Modéré
        589,  # Niveau rouge - Difficile
        590,  # Niveau noir - Très difficile
        6669,  # Niveau orange - assez difficile
    ]

    guidebook_description_id = 6527
    default_trek_marking_description = {
        "libelleFr": "Cet itinéraire est balisé.",
        "libelleEn": "This trek is marked.",
    }
    trek_no_marking_description = {
        "libelleFr": "Cet itinéraire n'est pas balisé",
        "libelleEn": "This trek is not marked",
    }

    def __init__(self, *args, **kwargs):
        self._related_treks_mapping = defaultdict(list)
        super().__init__(*args, **kwargs)

    def apply_filter(self, dst, src, val):
        val = super().apply_filter(dst, src, val)
        # Can be called after a filter_*** to dispatch translated values into translation fields.
        if dst in self.translated_fields:
            if isinstance(val, dict) or isinstance(val, ApidaeTranslatedField):
                if isinstance(val, ApidaeTranslatedField):
                    val = val.to_dict()

                for key, final_value in val.items():
                    if key in settings.MODELTRANSLATION_LANGUAGES:
                        self.set_value(f"{dst}_{key}", src, final_value)

                val = val.get(get_language())
        return val

    def add_warning(self, msg):
        key = _("APIDAE Trek #%(eid_val)s at line %(line)s") % {
            "eid_val": self.eid_val,
            "line": self.line,
        }
        warnings = self.warnings.setdefault(key, [])
        warnings.append(msg)

    def end(self):
        self._finalize_related_treks_association()
        super().end()

    def filter_eid(self, src, val):
        return str(val)

    def filter_geom(self, src, val):
        supported_extensions = ["gpx", "kml", "kmz"]
        plan = self._find_first_plan_with_supported_file_extension(
            val, supported_extensions
        )
        geom_file = self._fetch_geometry_file(plan)

        ext = self._get_plan_extension(plan)
        try:
            if ext == "gpx":
                return get_geom_from_gpx(geom_file)
            elif ext == "kml":
                return get_geom_from_kml(geom_file)
            elif ext == "kmz":
                kml_file = zipfile.ZipFile(io.BytesIO(geom_file)).read("doc.kml")
                return get_geom_from_kml(kml_file)
        except GeomValueError as e:
            raise RowImportError(str(e))

    def filter_labels(self, src, val):
        typologies, environnements = val
        translation_src = self._get_default_translation_src()
        filtered_val = []
        if typologies:
            filtered_val += [
                t[translation_src]
                for t in typologies
                if t["id"] in self.typologies_sitra_ids_as_labels
            ]
        if environnements:
            filtered_val += [
                e[translation_src]
                for e in environnements
                if e["id"] in self.environnements_ids_as_labels
            ]
        return self.apply_filter(dst="labels", src=src, val=filtered_val)

    def filter_themes(self, src, val):
        translation_src = self._get_default_translation_src()
        return self.apply_filter(
            dst="themes",
            src=src,
            val=[
                item[translation_src]
                for item in val
                if item["id"] in self.typologies_sitra_ids_as_themes
            ],
        )

    def filter_description(self, src, val):
        ouverture, descriptifs, itineraire, tarifs, moyen_communication = val
        return self.apply_filter(
            dst="description",
            src=src,
            val=self.__class__._make_description(
                ouverture, descriptifs, itineraire, tarifs, moyen_communication
            ),
        )

    def filter_source(self, src, val):
        manager = val
        sources = self.apply_filter(dst="source", src=src, val=[manager["nom"]])
        source = sources[0]
        source.website = manager.get("siteWeb")
        source.save()
        return sources

    def filter_difficulty(self, src, val):
        types_clientele = val
        difficulty_level = None
        for tc in types_clientele:
            if tc["id"] in self.types_clientele_ids_as_difficulty_levels:
                difficulty_level = tc
                break
        if difficulty_level:
            translation_src = self._get_default_translation_src()
            return self.apply_filter(
                dst="difficulty", src=src, val=difficulty_level[translation_src]
            )

    def save_trek_children(self, src, val):
        liens = val
        for lien in liens:
            if lien["type"] == "PARCOURS_ETAPE":
                child_trek = lien["objetTouristique"]
                self._related_treks_mapping[self.obj.id].append(child_trek["id"])

        # Always return "No changes" because one cannot know until the end which children trek are actually imported
        return False

    def filter_practice(self, src, val):
        activities = val
        activities_ids = [act["id"] for act in activities]
        return self.apply_filter(
            dst="practice",
            src=src,
            val=self._get_practice_name_from_activities(activities_ids),
        )

    def filter_networks(self, src, val):
        activities = val
        default_translation_fieldname = self._get_default_translation_src()
        filtered_activities = []
        for activity in activities:
            if default_translation_fieldname in activity:
                filtered_activities.append(activity[default_translation_fieldname])
        return self.apply_filter(dst="networks", src=src, val=filtered_activities)

    def filter_attachments(self, src, val):
        translation_src = self._get_default_translation_src()
        illustrations = val
        rv = []
        for illustration in illustrations:
            if not ApidaeTrekParser._is_still_publishable_tomorrow(
                illustration
            ) or not illustration.get("traductionFichiers"):
                continue
            rv.append(
                _prepare_attachment_from_apidae_illustration(
                    illustration, translation_src
                )
            )
        return rv

    def filter_duration(self, src, val):
        duree_journaliere, duree_itinerance = val
        return ApidaeTrekParser._make_duration(
            duration_in_minutes=duree_journaliere, duration_in_days=duree_itinerance
        )

    def filter_accessibilities(self, src, val):
        translation_fieldname = self._get_default_translation_src()
        return self.apply_filter(
            dst="accessibilities",
            src=src,
            val=[
                item[translation_fieldname]
                for item in val
                if item["id"]
                in ApidaeTrekParser.natures_de_terrain_ids_as_accessibilities
            ],
        )

    def filter_accessibility_covering(self, src, val):
        natures_terrain = val
        natures_terrain_ids_as_coverings = [
            4240,  # Cailloux
            4243,  # Gravillons
            4242,  # Revêtement dur (goudron, ciment, plancher)
            4239,  # Rocher
            4241,  # Terre
        ]
        filtered_nt = [
            nt for nt in natures_terrain if nt["id"] in natures_terrain_ids_as_coverings
        ]

        tf = ApidaeTranslatedField(separator=", ")
        for nt in filtered_nt:
            tf.append(translated_value=nt)
        return self.apply_filter(dst="accessibility_covering", src=src, val=tf)

    def filter_gear(self, src, val):
        ref_carto, ref_topo = val
        if not ref_carto and not ref_topo:
            return None
        tf = ApidaeTranslatedField()
        if ref_carto:
            tf.append(
                translated_value=ref_carto,
                transform_func=ApidaeTrekParser._transform_description_to_html,
            )
        if ref_topo:
            tf.append(
                translated_value=ref_topo,
                transform_func=ApidaeTrekParser._transform_description_to_html,
            )
        return self.apply_filter(dst="gear", src=src, val=tf)

    def _finalize_related_treks_association(self):
        for parent_id, children_eids in self._related_treks_mapping.items():
            parent_trek = Trek.objects.get(pk=parent_id)
            order = 0
            for child_eid in children_eids:
                try:
                    child_trek = Trek.objects.get(eid=child_eid)
                except Trek.DoesNotExist:
                    # It is possible that the child trek is not part of the import,
                    # if so just ignore it and do not create the link.
                    continue
                otc, _ = OrderedTrekChild.objects.get_or_create(
                    parent=parent_trek, child=child_trek
                )
                otc.order = order
                otc.save()
                order += 1

    def _fetch_geometry_file(self, plan):
        ref_fichier_plan = plan["traductionFichiers"][0]
        response = self.request_or_retry(url=ref_fichier_plan["url"])
        return response.content

    @classmethod
    def _transform_description_to_html(cls, text):
        """Transform a descriptive text into HTML paragraphs."""
        html_blocks = []
        lines = text.replace("\r", "").split("\n")
        for line in lines:
            if not line:
                continue
            html_blocks.append(f"<p>{line}</p>")
        return "".join(html_blocks)

    @classmethod
    def _transform_guidebook_to_html(cls, text):
        # This method can be overridden in var/conf/parsers.py.
        # FIXME: is there a better way to provide specific behaviors for parsing?
        return cls._transform_description_to_html(text)

    @classmethod
    def _assemble_infos_contact_to_html(cls, info_pieces):
        """Format "infos contact" into an HTML paragraph with break lines."""
        rv = defaultdict(list)

        def append_translated_values(info_piece):
            info_type = info_piece["type"]
            info_value = info_piece["coordonnees"]["fr"]
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                src = f"libelle{lang.capitalize()}"
                info_label = info_type.get(src)
                if info_label:
                    rv[src].append(f"<strong>{info_label}:</strong>{info_value}")

        ordered_info_type_ids = [
            205,  # Site web (URL)
            207,  # Page facebook
            201,  # Téléphone
            204,  # Mél
        ]
        for info_type_id in ordered_info_type_ids:
            for info_piece in info_pieces:
                if info_piece["type"]["id"] == info_type_id:
                    append_translated_values(info_piece)

        # Not specifically ordered info types go at the end
        for info_piece in info_pieces:
            if info_piece["type"]["id"] not in ordered_info_type_ids:
                append_translated_values(info_piece)

        for key, value in rv.items():
            rv[key] = "<p>" + "<br>".join(value) + "</p>"

        return rv

    @classmethod
    def _make_marking_description(cls, itineraire):
        is_marked = itineraire["itineraireBalise"] == "BALISE"
        if is_marked:
            marking_description = cls.default_trek_marking_description.copy()
            if itineraire.get("precisionsBalisage"):
                marking_description.update(itineraire["precisionsBalisage"])
        else:
            marking_description = cls.trek_no_marking_description.copy()
        return marking_description

    @staticmethod
    def _find_first_plan_with_supported_file_extension(items, supported_extensions):
        plans = [item for item in items if item["type"] == "PLAN"]
        if not plans:
            msg = 'The trek from APIDAE has no attachment with the type "PLAN"'
            raise RowImportError(msg)
        supported_plans = [
            plan
            for plan in plans
            if ApidaeTrekParser._get_plan_extension(plan) in supported_extensions
        ]
        if not supported_plans:
            msg = (
                'The trek from APIDAE has no attached "PLAN" in a supported format. '
                f"Supported formats are : {', '.join(supported_extensions)}"
            )
            raise RowImportError(msg)
        return supported_plans[0]

    @staticmethod
    def _get_plan_extension(plan):
        info_fichier = plan["traductionFichiers"][0]
        extension_prop = info_fichier.get("extension")
        if extension_prop:
            return extension_prop
        url_suffix = PurePath(info_fichier["url"]).suffix
        if url_suffix:
            return url_suffix.split(".")[1]
        return None

    @staticmethod
    def _find_matching_practice_in_mapping(activities_ids, mapping):
        returned_practice_name = None
        for activity_id in activities_ids:
            for practice_name, value in mapping.items():
                try:
                    for mapped_activity_id in value:
                        if activity_id == mapped_activity_id:
                            returned_practice_name = practice_name
                except TypeError:
                    mapped_activity_id = value
                    if activity_id == mapped_activity_id:
                        returned_practice_name = practice_name
        return returned_practice_name

    @classmethod
    def _get_practice_name_from_activities(cls, activities_ids):
        for mapping in (
            cls.practices_mapped_with_activities_ids,
            cls.practices_mapped_with_default_activities_ids,
        ):
            practice_name = ApidaeTrekParser._find_matching_practice_in_mapping(
                activities_ids, mapping
            )
            if practice_name:
                break
        return practice_name

    @staticmethod
    def _is_still_publishable_tomorrow(illustration):
        # The illustration is still publishable tomorrow if tomorrow is strictly before the limit date.
        # This is to ensure the next import will always occur before the time part of the limit date.
        return ApidaeTrekParser._is_still_publishable_on(
            illustration, date.today() + timedelta(days=1)
        )

    @staticmethod
    def _is_still_publishable_on(illustration, a_date):
        max_datetime_str = illustration.get("dateLimiteDePublication")
        if not max_datetime_str:
            return True
        # Regexp parsing because Python does not handle timezone with no colon,
        # and because we don't know when the import is run we drop the time part.
        result = re.match(r"(\d{4})-(\d{2})-(\d{2})", max_datetime_str)
        year, month, day = map(int, result.groups())
        max_date = date(year, month, day)
        # Note this exludes the limit date.
        return max_date > a_date

    @classmethod
    def _make_description(
        cls,
        ouverture=None,
        descriptifs=None,
        itineraire=None,
        tarifs=None,
        infos_contact=None,
    ):
        def get_guidebook():
            if not descriptifs:
                return None
            for d in descriptifs:
                if d["theme"]["id"] == cls.guidebook_description_id:
                    return d
            return None

        def est_fermé_temporairement(ouverture):
            return ouverture.get("fermeTemporairement") == "FERME_TEMPORAIREMENT"

        tf = ApidaeTranslatedField()

        if ouverture and est_fermé_temporairement(ouverture):
            tf.append(
                translated_value=ouverture["periodeEnClair"],
                transform_func=cls._transform_description_to_html,
            )

        guidebook = get_guidebook()
        if guidebook:
            tf.append(
                translated_value=guidebook["description"],
                transform_func=cls._transform_guidebook_to_html,
            )

        if ouverture and not est_fermé_temporairement(ouverture):
            tf.append(
                translated_value=ouverture["periodeEnClair"],
                transform_func=cls._transform_description_to_html,
            )

        if itineraire:
            tf.append(
                translated_value=cls._make_marking_description(itineraire),
                transform_func=cls._transform_description_to_html,
            )

        if tarifs and tarifs["indicationTarif"] == "PAYANT":
            tf.append(
                translated_value=tarifs["tarifsEnClair"],
                transform_func=cls._transform_description_to_html,
            )

        if infos_contact:
            tf.append(
                translated_value=cls._assemble_infos_contact_to_html(infos_contact)
            )

        return tf

    @staticmethod
    def _make_duration(duration_in_minutes=None, duration_in_days=None):
        """Returns the duration in hours. There are 2 use cases:

        1. the parsed trek is a one-day trip: only the duration in minutes is provided from Apiade.
        2. the parsed trek is a multiple-day trip: the duration_in_days is provided. The duration_in_minutes may be provided
          as a crude indication of how long each step is. That second value does not fit in Geotrek model.

        So the duration_in_days is used if provided (and duration_in_minutes discarded), it means we are in the use case 2.
        Otherwise the duration_in_minutes is used, it means use case 1.
        """
        if duration_in_days:
            return float(duration_in_days * 24)
        elif duration_in_minutes:
            return float(
                (Decimal(duration_in_minutes) / Decimal(60)).quantize(Decimal(".01"))
            )
        else:
            return None


class ApidaeReferenceElementParser(Parser):
    url = "https://api.apidae-tourisme.com/api/v002/referentiel/elements-reference/"

    api_key = None
    project_id = None
    element_reference_ids = None
    name_field = None
    # Fields mapping is generated in __init__

    def __init__(self, *args, **kwargs):
        self._add_multi_languages_fields_mapping()
        self._set_eid_fieldname()
        super().__init__(*args, **kwargs)

    def _add_multi_languages_fields_mapping(self):
        self.fields = {
            build_localized_fieldname(
                self.name_field, lang
            ): f"libelle{lang.capitalize()}"
            for lang in settings.MODELTRANSLATION_LANGUAGES
        }

    def _set_eid_fieldname(self):
        self.eid = build_localized_fieldname(
            self.name_field, settings.MODELTRANSLATION_DEFAULT_LANGUAGE
        )

    @property
    def items(self):
        return self.root

    def next_row(self):
        params = {
            "apiKey": self.api_key,
            "projetId": self.project_id,
            "elementReferenceIds": self.element_reference_ids,
        }
        response = self.request_or_retry(self.url, params={"query": json.dumps(params)})
        self.root = response.json()
        self.nb = len(self.root)
        yield from self.items

    def normalize_field_name(self, name):
        return name


class ApidaeTrekThemeParser(ApidaeReferenceElementParser):
    model = Theme
    element_reference_ids = ApidaeTrekParser.typologies_sitra_ids_as_themes
    name_field = "label"


class ApidaeTrekLabelParser(ApidaeReferenceElementParser):
    model = Label
    element_reference_ids = (
        ApidaeTrekParser.typologies_sitra_ids_as_labels
        + ApidaeTrekParser.environnements_ids_as_labels
    )
    name_field = "name"


class ApidaeTrekDifficultyParser(ApidaeReferenceElementParser):
    model = DifficultyLevel
    element_reference_ids = ApidaeTrekParser.types_clientele_ids_as_difficulty_levels
    name_field = "difficulty"


class ApidaeTrekNetworkParser(ApidaeReferenceElementParser):
    model = TrekNetwork
    element_reference_ids = ApidaeTrekParser.activites_ids_as_networks
    name_field = "network"


class ApidaeTrekAccessibilityParser(ApidaeReferenceElementParser):
    model = Accessibility
    element_reference_ids = ApidaeTrekParser.natures_de_terrain_ids_as_accessibilities
    name_field = "name"


class ApidaePOIParser(AttachmentParserMixin, ApidaeBaseTrekkingParser):
    model = POI
    eid = "eid"
    separator = None

    # Parameters to build the request
    api_key = None
    project_id = None
    selection_id = None
    size = 20
    skip = 0
    responseFields = [
        "id",
        "nom",
        "presentation",
        "localisation",
        "informationsPatrimoineCulturel",
        "illustrations",
    ]
    locales = ["fr", "en"]

    # Fields mapping
    fill_empty_translated_fields = True
    fields = {
        "name": "nom",
        "description": "presentation.descriptifCourt",
        "geom": "localisation.geolocalisation.geoJson",
        "eid": "id",
        "type": "type",
    }
    natural_keys = {
        "type": "label",
    }
    field_options = {
        "type": {"create": True},
        "name": {"expand_translations": True},
        "description": {"expand_translations": True},
    }
    non_fields = {"attachments": "illustrations"}

    def filter_type(self, src, val):
        type_label = val.replace("_", " ").lower().capitalize()
        return self.apply_filter(dst="type", src=src, val=type_label)

    def filter_geom(self, src, val):
        geom = GEOSGeometry(str(val))
        geom.transform(settings.SRID)
        return geom

    def filter_attachments(self, src, val):
        translation_src = self._get_default_translation_src()
        illustrations = val
        rv = []
        for illustration in illustrations:
            if not illustration.get("traductionFichiers"):
                continue
            rv.append(
                _prepare_attachment_from_apidae_illustration(
                    illustration, translation_src
                )
            )
        return rv


class ApidaeServiceParser(ApidaeBaseParser):
    model = Service
    eid = "eid"
    service_type = None

    responseFields = [
        "id",
        "localisation.geolocalisation.geoJson",
    ]

    fields = {
        "eid": "id",
        "geom": "localisation.geolocalisation.geoJson",
    }
    natural_keys = {
        "type": "name",
    }
    field_options = {
        "type": {"create": True},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.service_type:
            self.constant_fields = self.constant_fields.copy()
            self.constant_fields["type"] = self.service_type
        else:
            raise ImproperlyConfigured(
                _("A service type must be defined in parser configuration.")
            )

    def filter_geom(self, src, val):
        try:
            geom = GEOSGeometry(str(val))
            geom.transform(settings.SRID)
        except Exception:
            raise RowImportError(
                _("Could not parse geometry from value '{value}'").format(value=val)
            )
        return geom


class SchemaRandonneeParser(AttachmentParserMixin, Parser):
    """Parser for v1.1.0 of schema_randonnee: https://github.com/PnX-SI/schema_randonnee/tree/v1.1.0"""

    model = Trek
    eid = "eid"
    separator = ","
    srid = 4326

    fields = {
        "eid": ("uuid", "id_local"),
        "name": "nom_itineraire",
        "geom": "geometry",
        "practice": "pratique",
        "route": "type_itineraire",
        "departure": "depart",
        "arrival": "arrivee",
        "duration": "duree",
        "difficulty": "difficulte",
        "description": ("instructions", "url"),
        "ambiance": "presentation",
        "description_teaser": "presentation_courte",
        "advice": "recommandations",
        "accessibility_advice": "accessibilite",
        "accessibility_covering": "type_sol",
        "access": "acces_routier",
        "public_transport": "transports_commun",
        "advised_parking": "parking_info",
        "parking_location": "parking_geometrie",
    }
    m2m_fields = {
        "source": "producteur",
        "themes": "themes",
        "networks": "balisage",
    }
    natural_keys = {
        "source": "name",
        "practice": "name",
        "route": "route",
        "difficulty": "difficulty",
        "themes": "label",
        "networks": "network",
    }
    field_options = {
        "practice": {
            "mapping": {
                "pédestre": "Pédestre",
                "autre": "Pédestre",
                "trail": "Trail",
                "gravel": "Vélo",
                "VTT": "Vélo",
                "cyclo": "Vélo",
                "équestre": "Equestre",
                "ski de fond": "Ski de fond",
                "ski de rando": "Ski de rando",
                "raquettes": "Raquettes",
            },
        },
        "route": {
            "mapping": {
                "aller-retour": "Aller-retour",
                "boucle": "Boucle",
                "aller simple": "Aller simple",
                "itinérance": "Itinérance",
                "étape": "Etape",
            },
        },
    }
    non_fields = {
        "attachments": "medias",
        "id_local": "id_local",
        "itineraire_parent": "itineraire_parent",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.related_treks_mapping = defaultdict(list)
        self.id_local_to_pk_mapping = {}
        if self.url:
            response = self.request_or_retry(self.url)
            self.root = response.json()
            self.items = self.root["features"]
            self.nb = len(self.items)

    def parse(self, filename=None, limit=None):
        if filename:
            self.filename = filename
            with open(self.filename) as f:
                self.root = json.load(f)
                self.items = self.root["features"]
                self.nb = len(self.items)
        super().parse(filename=filename, limit=limit)

    def normalize_field_name(self, name):
        return name

    def next_row(self):
        for row in self.items:
            properties = row["properties"]
            properties["geometry"] = row.get("geometry")
            yield properties

    def filter_eid(self, src, val):
        uuid, id_local = val
        if uuid:
            return uuid
        return id_local

    def filter_geom(self, src, val):
        if val is None:
            raise RowImportError(_("Trek geometry is None"))
        if val.get("type") != "LineString":
            raise RowImportError(
                _(
                    "Invalid geometry type for field '{src}'. Should be LineString, not {geom_type}"
                ).format(src=src, geom_type=val.get("type"))
            )
        try:
            geom = LineString(val["coordinates"], srid=self.srid)
        except KeyError:
            raise RowImportError(
                _(
                    "Invalid geometry for field '{src}'. Should contain coordinates"
                ).format(src=src)
            )
        geom.transform(settings.SRID)
        return geom

    def filter_parking_location(self, src, val):
        if val is None:
            return None
        try:
            point = GEOSGeometry(val, srid=self.srid)
            if not isinstance(point, Point):
                raise ValueError
            point.transform(settings.SRID)
            return point
        except ValueError:
            self.add_warning(_("Bad value for parking geometry: should be a Point"))

    def filter_description(self, src, val):
        instructions, url = val
        if not instructions and not url:
            return None
        description = ""
        if instructions:
            description += instructions
        if instructions and url:
            description += "\n\n"
        if url:
            description += f"<a href={url}>{url}</a>"
        return description

    def filter_attachments(self, src, val):
        """Handles images only"""
        if val is None:
            return []
        attachments = []
        for media in val:
            if media.get("url") is None or media.get("type_media") != "image":
                continue
            attachments.append(
                (
                    media.get("url"),
                    media.get("titre"),
                    media.get("auteur"),
                    media.get("titre"),
                    media.get("licence"),
                )
            )
        return attachments

    def generate_attachments(self, src, val, attachments_to_delete, updated):
        attachments = []
        for url, legend, author, title, license_label in self.filter_attachments(
            src, val
        ):
            url = self.base_url + url
            legend = legend or ""
            author = author or ""
            title = title or ""
            license = self.get_or_create_license(license_label)
            basename, ext = os.path.splitext(os.path.basename(url))
            name = f"{basename[:128]}{ext}"
            found, updated = self.check_attachment_updated(
                attachments_to_delete,
                updated,
                name=name,
                url=url,
                legend=legend,
                author=author,
                title=title,
                license_label=license_label,
            )
            if found:
                continue

            parsed_url = urlparse(url)
            attachment = self.generate_attachment(
                author=author, legend=legend, title=title, license=license
            )
            try:
                save, updated = self.generate_content_attachment(
                    attachment, parsed_url, url, updated, name
                )
                if not save:
                    continue
            except ValueImportError as warning:
                self.add_warning(str(warning))
                continue
            attachments.append(attachment)
            updated = True
        return updated, attachments

    def generate_attachment(self, **kwargs):
        attachment = Attachment()
        attachment.content_object = self.obj
        attachment.filetype = self.filetype
        attachment.creator = self.creator
        attachment.author = kwargs.get("author")
        attachment.legend = textwrap.shorten(kwargs.get("legend", ""), width=127)
        attachment.license = kwargs.get("license")
        attachment.title = textwrap.shorten(kwargs.get("title", ""), width=127)
        return attachment

    def check_attachment_updated(self, attachments_to_delete, updated, **kwargs):
        found = False
        for attachment in attachments_to_delete:
            upload_name, ext = os.path.splitext(
                attachment_upload(attachment, kwargs.get("name"))
            )
            existing_name = attachment.attachment_file.name
            regexp = (
                f"{upload_name}({random_suffix_regexp()})?(_[a-zA-Z0-9]{{7}})?{ext}"
            )
            if re.search(rf"^{regexp}$", existing_name) and not self.has_size_changed(
                kwargs.get("url"), attachment
            ):
                found = True
                attachments_to_delete.remove(attachment)
                if (
                    kwargs.get("author") != attachment.author
                    or kwargs.get("legend") != attachment.legend
                    or kwargs.get("title") != attachment.title
                    or (kwargs.get("license_label") and not attachment.license)
                    or (
                        attachment.license
                        and kwargs.get("license_label") != attachment.license.label
                    )
                ):
                    attachment.author = kwargs.get("author")
                    attachment.legend = textwrap.shorten(
                        kwargs.get("legend"), width=127
                    )
                    attachment.title = textwrap.shorten(kwargs.get("title"), width=127)
                    attachment.license = self.get_or_create_license(
                        kwargs.get("license_label")
                    )
                    attachment.save(**{"skip_file_save": True})
                    updated = True
                break
        return found, updated

    def get_or_create_license(self, license_label):
        license = None
        if license_label is not None:
            try:
                license = License.objects.get(label=license_label)
            except License.DoesNotExist:
                attachment_options = self.field_options.get("attachments")
                if attachment_options and attachment_options.get("create_license"):
                    license = License.objects.create(label=license_label)
                    self.add_warning(
                        _(
                            "License '{val}' did not exist in Geotrek-Admin and was automatically created"
                        ).format(val=license_label)
                    )
                else:
                    self.add_warning(
                        _(
                            "License '{val}' does not exist in Geotrek-Admin. Please add it"
                        ).format(val=license_label)
                    )
        return license

    def save_id_local(self, src, val):
        if val:
            self.id_local_to_pk_mapping[val] = self.obj.pk

    def save_itineraire_parent(self, src, val):
        if val:
            self.related_treks_mapping[val].append(self.obj.pk)

    def end(self):
        """
        After all treks have been created, add parent/children relationships
        """
        for parent_id_local, child_pks in self.related_treks_mapping.items():
            parent_pk = self.id_local_to_pk_mapping.get(parent_id_local)
            try:
                parent_trek = Trek.objects.get(pk=parent_pk)
            except Trek.DoesNotExist:
                continue
            order = 0
            for child_pk in child_pks:
                child_trek = Trek.objects.get(pk=child_pk)
                otc, _ = OrderedTrekChild.objects.get_or_create(
                    parent=parent_trek, child=child_trek
                )
                otc.order = order
                otc.save()
                order += 1
        super().end()


class OpenStreetMapPOIParser(OpenStreetMapAttachmentsParserMixin, OpenStreetMapParser):
    """Parser to import POI from OpenStreetMap"""

    type = None
    model = POI
    eid = "eid"

    fields = {
        "eid": ("type", "id"),  # ids are unique only for object of the same type
        "name": "tags.name",
        "description": "tags.description",
        "geom": ("type", "lon", "lat", "geometry", "bounds"),
    }
    constant_fields = {
        "published": True,
    }
    natural_keys = {
        "type": "label",
    }
    field_options = {"geom": {"required": True}, "type": {"required": True}}
    topology = Topology.objects.none()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.type:
            self.constant_fields["type"] = self.type

    def start(self):
        super().start()
        if settings.TREKKING_TOPOLOGY_ENABLED and not Path.objects.exists():
            raise GlobalImportError(
                _("You need to add a network of paths before importing POIs")
            )

    def filter_geom(self, src, val):
        # convert OSM geometry to point
        type, lng, lat, area, bbox = val
        geom = None
        if type == "node":
            geom = Point(float(lng), float(lat), srid=self.osm_srid)  # WGS84
        elif type == "way":
            geom = self.get_centroid_from_way(area)
        elif type == "relation":
            geom = self.get_centroid_from_relation(bbox)

        # create topology
        self.topology = Topology.objects.none()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Use existing topology helpers to transform a Point(x, y)
            # to a path aggregation (topology)
            serialized = f'{{"lng": {geom.x}, "lat": {geom.y}}}'
            self.topology = Topology.deserialize(serialized)
            # Move deserialization aggregations to the POI
        geom.transform(settings.SRID)
        return geom

    def parse_obj(self, row, operation):
        super().parse_obj(row, operation)
        if settings.TREKKING_TOPOLOGY_ENABLED and self.obj.geom and self.topology:
            self.obj.mutate(self.topology)
