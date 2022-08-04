import json
from django.conf import settings
from django.contrib.gis.geos import Point, GEOSGeometry
from django.utils.translation import gettext as _

from geotrek.common.parsers import ShapeParser, AttachmentParserMixin, GeotrekParser
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
        'networks': 'network',
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
    url = None
    model = Trek
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    replace_fields = {
        "eid": "id",
        "eid2": "second_external_id",
        "geom": "geometry"
    }
    url_categories = {
        "difficulty": "/api/v2/trek_difficulty/",
        "route": "/api/v2/trek_route/",
        "themes": "/api/v2/theme/",
        "practice": "/api/v2/trek_practice/",
        "accessibilities": "/api/v2/trek_accessibility/",
        "networks": "/api/v2/trek_network/",
        'labels': '/api/v2/label/'
    }
    categories_keys_api_v2 = {
        'difficulty': 'label',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'label',
        'labels': 'name'
    }
    natural_keys = {
        'difficulty': 'difficulty',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'network',
        'labels': 'name'
    }

    def next_row(self):
        self.next_url = f"{self.url}/api/v2/trek"
        return super().next_row()

    def filter_parking_location(self, src, val):
        if val:
            return Point(val[0], val[1], srid=settings.API_SRID)

    def filter_points_reference(self, src, val):
        if val:
            geom = GEOSGeometry(json.dumps(val))
            return geom.transform(settings.SRID, clone=True)

    def end(self):
        super().end()
        self.next_url = f"{self.url}/api/v2/trek"
        try:
            params = {
                'in_bbox': ','.join([str(coord) for coord in self.bbox.extent]),
                'fields': 'children,id'
            }
            response = self.request_or_retry(f"{self.next_url}", params=params)
            results = response.json()['results']
            final_children = {}
            for result in results:
                final_children[result['id']] = result['children']

            for key, value in final_children.items():
                if value:
                    trek_parent_instance = Trek.objects.filter(eid=f"{self.eid_prefix}{key}")
                    if not trek_parent_instance:
                        return
                    order = 0
                    for child in value:
                        try:
                            trek_child_instance = Trek.objects.get(eid=f"{self.eid_prefix}{child}")
                        except Trek.DoesNotExist:
                            self.add_warning(_(f"One trek has not be generated for {trek_parent_instance[0].name}"))
                            continue
                        OrderedTrekChild.objects.get_or_create(parent=trek_parent_instance[0],
                                                               child=trek_child_instance,
                                                               order=order)
                        order += 1
        except Exception as e:
            self.add_warning(_(f"An error occured in children generation : {e}"))


class GeotrekServiceParser(GeotrekParser):
    url = None
    model = Service
    constant_fields = {
        'deleted': False,
    }
    replace_fields = {
        "eid": "id",
        "geom": "geometry"
    }
    url_categories = {
        "type": "/api/v2/service_type/",
    }
    categories_keys_api_v2 = {
        'type': 'name',
    }
    natural_keys = {
        'type': 'name'
    }

    def next_row(self):
        self.next_url = f"{self.url}/api/v2/service"
        return super().next_row()


class GeotrekPOIParser(GeotrekParser):
    url = None
    model = POI
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    replace_fields = {
        "eid": "id",
        "geom": "geometry"
    }
    url_categories = {
        "type": "/api/v2/poi_type/",
    }
    categories_keys_api_v2 = {
        'type': 'label',
    }
    natural_keys = {
        'type': 'label',
    }

    def next_row(self):
        self.next_url = f"{self.url}/api/v2/poi"
        return super().next_row()
