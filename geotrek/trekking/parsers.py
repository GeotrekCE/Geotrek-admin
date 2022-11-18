import json
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point, GEOSGeometry
from django.utils.translation import gettext as _

from geotrek.common.parsers import ShapeParser, AttachmentParserMixin, GeotrekParser, RowImportError
from geotrek.trekking.models import OrderedTrekChild, POI, Service, Trek


class DurationParserMixin:
    def filter_duration(self, src, val):
        val = val.upper().replace(',', '.')
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
            self.add_warning(_("Bad value '{val}' for field {src}. Should be like '2h30', '2,5' or '2.5'".format(val=val, src=src)))
            return None


class TrekParser(DurationParserMixin, AttachmentParserMixin, ShapeParser):
    label = "Import trek"
    label_fr = "Import itinéraires"
    label_en = "Import trek"
    model = Trek
    simplify_tolerance = 2
    eid = 'name'
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    natural_keys = {
        'difficulty': 'difficulty',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'network'
    }

    def filter_geom(self, src, val):
        if val is None:
            return None
        if val.geom_type == 'MultiLineString':
            points = val[0]
            for i, path in enumerate(val[1:]):
                distance = Point(points[-1]).distance(Point(path[0]))
                if distance > 5:
                    self.add_warning(_("Not contiguous segment {i} ({distance} m) for geometry for field '{src}'").format(i=i + 2, p1=points[-1], p2=path[0], distance=int(distance), src=src))
                points += path
            return points
        elif val.geom_type != 'LineString':
            self.add_warning(_("Invalid geometry type for field '{src}'. Should be LineString, not {geom_type}").format(src=src, geom_type=val.geom_type))
            return None
        return val


class GeotrekTrekParser(GeotrekParser):
    """Geotrek parser for Trek"""

    url = None
    model = Trek
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    replace_fields = {
        "eid": "uuid",
        "eid2": "second_external_id",
        "geom": "geometry"
    }
    url_categories = {
        "difficulty": "trek_difficulty",
        "route": "trek_route",
        "themes": "theme",
        "practice": "trek_practice",
        "accessibilities": "trek_accessibility",
        "networks": "trek_network",
        'labels': 'label',
        'source': 'source'
    }
    categories_keys_api_v2 = {
        'difficulty': 'label',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'label',
        'labels': 'name',
        'source': 'name'
    }
    natural_keys = {
        'difficulty': 'difficulty',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'network',
        'labels': 'name',
        'source': 'name'
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

    def end(self):
        """Add children after all treks imported are created in database."""
        super().end()
        self.next_url = f"{self.url}/api/v2/tour"
        try:
            params = {
                'in_bbox': ','.join([str(coord) for coord in self.bbox.extent]),
                'fields': 'steps,uuid'
            }
            response = self.request_or_retry(f"{self.next_url}", params=params)
            results = response.json()['results']
            final_children = {}
            for result in results:
                final_children[result['uuid']] = [step['uuid'] for step in result['steps']]

            for key, value in final_children.items():
                if value:
                    trek_parent_instance = Trek.objects.filter(eid=key)
                    if not trek_parent_instance:
                        self.add_warning(_(f"Trying to retrieve children for missing trek : could not find trek with UUID {key}"))
                        return
                    order = 0
                    for child in value:
                        try:
                            trek_child_instance = Trek.objects.get(eid=child)
                        except Trek.DoesNotExist:
                            self.add_warning(_(f"One trek has not be generated for {trek_parent_instance[0].name} : could not find trek with UUID {child}"))
                            continue
                        OrderedTrekChild.objects.get_or_create(parent=trek_parent_instance[0],
                                                               child=trek_child_instance,
                                                               order=order)
                        order += 1
        except Exception as e:
            self.add_warning(_(f"An error occured in children generation : {getattr(e, 'message', repr(e))}"))


class GeotrekServiceParser(GeotrekParser):
    """Geotrek parser for Service"""

    url = None
    model = Service
    constant_fields = {
        'deleted': False,
    }
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry"
    }
    url_categories = {
        "type": "service_type",
    }
    categories_keys_api_v2 = {
        'type': 'name',
    }
    natural_keys = {
        'type': 'name'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/service"


class GeotrekPOIParser(GeotrekParser):
    """Geotrek parser for GeotrekPOI"""

    url = None
    model = POI
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry"
    }
    url_categories = {
        "type": "poi_type",
    }
    categories_keys_api_v2 = {
        'type': 'label',
    }
    natural_keys = {
        'type': 'label',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/poi"


from geotrek.tourism.parsers import ApidaeParser  # Noqa


TYPOLOGIES_SITRA_IDS_AS_LABELS = [1599, 1676, 4639, 4819, 5022, 4971, 3845, 6566, 6049, 1582, 5538, 6825, 6608, 1602]
TYPOLOGIES_SITRA_IDS_AS_THEMES = [6155, 6156, 6368, 6153, 6154, 6157, 6163, 6158, 6679, 6159, 6160, 6161]


class ApidaeTrekParser(ApidaeParser):
    model = Trek
    separator = None

    # Parameters to build the request
    url = 'https://api.apidae-tourisme.com/api/v002/recherche/list-objets-touristiques/'
    api_key = None
    project_id = None
    selection_id = None
    size = 20
    skip = 0
    responseFields = [
        'id',
        'nom',
        'multimedias',
        'gestion',
        'presentation',
    ]
    locales = ['fr', 'en']

    # Fields mapping
    fields = {
        'name_fr': 'nom.libelleFr',
        'name_en': 'nom.libelleEn',
        # retire la geom pour le moment car il y a des erreurs sur certains imports d'itinéraires
        # 'geom': 'multimedias',
        'eid': 'id',
    }
    m2m_fields = {
        'source': ['gestion.membreProprietaire.nom'],
        'themes': 'presentation.typologiesPromoSitra.*',
        'labels': 'presentation.typologiesPromoSitra.*',
    }
    natural_keys = {
        'source': 'name',
        'themes': 'label',
        'labels': 'name',
    }
    field_options = {
        'source': {'create': True},
        'themes': {'create': True},
        'labels': {'create': True},
    }
    non_fields = {}

    @staticmethod
    def _find_gpx_plan_in_multimedia_items(items):
        plans = list(filter(lambda item: item['type'] == 'PLAN', items))
        if len(plans) > 1:
            raise RowImportError("APIDAE Trek has more than one map defined")
        return plans[0]

    def _fetch_gpx_from_url(self, plan):
        ref_fichier_plan = plan['traductionFichiers'][0]
        if ref_fichier_plan['extension'] != 'gpx':
            raise RowImportError("Le plan de l'itinéraire APIDAE n'est pas au format GPX")
        response = self.request_or_retry(url=ref_fichier_plan['url'])
        # print('downloaded url {}, content size {}'.format(plan['traductionFichiers'][0]['url'], len(response.text)))
        return response.content

    @staticmethod
    def _get_tracks_layer(datasource):
        for layer in datasource:
            if layer.name == 'tracks':
                return layer
        raise RowImportError("APIDAE Trek GPX map does not have a 'tracks' layer")

    def filter_geom(self, src, val):
        plan = self._find_gpx_plan_in_multimedia_items(val)
        gpx = self._fetch_gpx_from_url(plan)

        # FIXME: is there another way than the temporary file? It seems not. `DataSource` really expects a filename.
        with NamedTemporaryFile(mode='w+b', dir='/opt/geotrek-admin/var/tmp') as ntf:
            ntf.write(gpx)
            ntf.flush()

            ds = DataSource(ntf.name)
            track_layer = self._get_tracks_layer(ds)
            geom = track_layer[0].geom[0].geos
            geom.transform(settings.SRID)
            return geom

    def filter_labels(self, src, val):
        return [item['libelleFr'] for item in val if item['id'] in TYPOLOGIES_SITRA_IDS_AS_LABELS]

    def filter_themes(self, src, val):
        return [item['libelleFr'] for item in val if item['id'] in TYPOLOGIES_SITRA_IDS_AS_THEMES]
