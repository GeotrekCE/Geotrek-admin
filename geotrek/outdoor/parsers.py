from django.conf import settings
from django.contrib.gis.geos import LineString, MultiPolygon, Point, Polygon
from django.contrib.gis.geos.collections import GeometryCollection

from geotrek.common.parsers import (
    GeotrekParser,
    OpenStreetMapAttachmentsParserMixin,
    OpenStreetMapParser,
    RowImportError,
)
from geotrek.outdoor.models import (
    Course,
    CourseType,
    OrderedCourseChild,
    Practice,
    Rating,
    RatingScale,
    Sector,
    Site,
    SiteType,
)
from geotrek.trekking.models import WebLink


class GeotrekOutdoorParser(GeotrekParser):
    def init_outdoor_category(
        self, category, model, join_field=None, extra_fields=None
    ):
        # Get categories as JSON response
        response = self.request_or_retry(
            f"{self.url}/api/v2/{self.init_url_categories[category]}"
        )
        results = response.json().get("results", [])

        # Init mapping variable for this category if it does not exist
        if category not in self.field_options.keys():
            self.field_options[category] = {}
        if "mapping" not in self.field_options[category].keys():
            self.field_options[category]["mapping"] = {}
        if self.create_categories:
            self.field_options[category]["create"] = True

        # Iter over category JSON results
        for result in results:
            # Extract label in default language from JSON
            label = result["name"]
            if isinstance(label, dict):
                if label[settings.MODELTRANSLATION_DEFAULT_LANGUAGE]:
                    replaced_label = self.replace_mapping(
                        label[settings.MODELTRANSLATION_DEFAULT_LANGUAGE],
                        self.init_url_categories[category],
                    )
            else:
                replaced_label = self.replace_mapping(
                    label, self.init_url_categories[category]
                )

            # Extract other category attributes in default language from JSON
            fields = {}
            if extra_fields is not None:
                for field in extra_fields:
                    if isinstance(result[field], dict):
                        if result[field][settings.MODELTRANSLATION_DEFAULT_LANGUAGE]:
                            fields[field] = result[field][
                                settings.MODELTRANSLATION_DEFAULT_LANGUAGE
                            ]
                    else:
                        fields[field] = result[field]

            # Extract field that will become a ForeignKey from JSON response, using mapping
            if join_field and result.get(join_field, False):
                mapped_value = self.get_id_from_mapping(
                    self.field_options[join_field]["mapping"], result[join_field]
                )
                if not mapped_value:
                    continue  # Ignore some results if related category was not retrieved
                fields[f"{join_field}_id"] = mapped_value

            # Create or update object given all the fields that we extracted above
            category_obj, _ = model.objects.update_or_create(
                **{"name": replaced_label}, defaults=fields
            )

            # Remember this object in mapping for next call
            self.update_mapping(category, category_obj.pk, result["id"])

    def update_mapping(self, category, key, value):
        # Ensure an ID only appears once in mapping
        obsolete_key = None
        for current_key, current_value in self.field_options[category][
            "mapping"
        ].items():
            if current_value == value and current_key != key:
                obsolete_key = current_key
        if obsolete_key:
            self.field_options[category]["mapping"].pop(obsolete_key)
        self.field_options[category]["mapping"][key] = value

    def get_id_from_mapping(self, mapping, value):
        for dest_id, source_id in mapping.items():
            if source_id == value:
                return dest_id
        return None

    def start(self):
        super().start()
        self.init_outdoor_category("sector", Sector)
        self.init_outdoor_category("practice", Practice, join_field="sector")
        self.init_outdoor_category("scale", RatingScale, join_field="practice")
        self.init_outdoor_category(
            "ratings",
            Rating,
            join_field="scale",
            extra_fields=["description", "order", "color"],
        )

    def filter_practice(self, src, val):
        if val:
            practice_id = self.get_id_from_mapping(
                self.field_options["practice"]["mapping"], val
            )
            if practice_id:
                return Practice.objects.get(pk=practice_id)
        return None

    def filter_ratings(self, src, val):
        ratings = []
        for subval in val:
            rating_id = self.get_id_from_mapping(
                self.field_options["ratings"]["mapping"], subval
            )
            if rating_id:
                ratings.append(Rating.objects.get(pk=rating_id))
        return ratings


class GeotrekSiteParser(GeotrekOutdoorParser):
    """Geotrek parser for Outoor Site"""

    fill_empty_translated_fields = True
    url = None
    model = Site
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry",
    }
    init_url_categories = {
        "sector": "outdoor_sector",
        "practice": "outdoor_practice",
        "scale": "outdoor_ratingscale",
        "ratings": "outdoor_rating",
        "type": "outdoor_sitetype",
    }
    url_categories = {
        "structure": "structure",
        "themes": "theme",
        "labels": "label",
        "source": "source",
        "managers": "organism",
    }
    categories_keys_api_v2 = {
        "structure": "name",
        "practice": "name",
        "sector": "name",
        "rating": "name",
        "scale": "name",
        "ratingscale": "name",
        "themes": "label",
        "type": "name",
        "labels": "name",
        "source": "name",
        "managers": "name",
    }
    natural_keys = {
        "structure": "name",
        "practice": "name",
        "themes": "label",
        "type": "name",
        "labels": "name",
        "source": "name",
        "managers": "organism",
    }

    def start_meta(self):
        super().start_meta()
        self.parents = {}
        self.next_url = f"{self.url}/api/v2/outdoor_site"

    def filter_type(self, src, val):
        if val:
            type_id = self.get_id_from_mapping(
                self.field_options["type"]["mapping"], val
            )
            if type_id:
                return SiteType.objects.get(pk=type_id)
        return None

    def start(self):
        super().start()
        self.init_outdoor_category("type", SiteType, join_field="practice")

    def parse_row(self, row):
        super().parse_row(row)
        self.parents[row["uuid"]] = row["parent_uuid"]

    def end(self):
        """Add children after all Sites imported are created in database."""
        for child, parent in self.parents.items():
            if parent:
                child_site = Site.objects.get(eid=child)
                try:
                    parent_site = Site.objects.get(eid=parent)
                except Site.DoesNotExist:
                    self.add_warning(
                        f"Trying to retrieve missing parent (UUID: {parent}) for child Site (UUID: {child})"
                    )
                    continue
                child_site.parent = parent_site
                child_site.save()
        if self.delete:
            # Prepare deletion by removing protected links
            for site in self.model.objects.filter(pk__in=self.to_delete):
                site.children.set([])
                site.children_courses.set([])
        super().end()


class GeotrekCourseParser(GeotrekOutdoorParser):
    """Geotrek parser for Outoor Course"""

    fill_empty_translated_fields = True
    url = None
    model = Course
    replace_fields = {"eid": "uuid", "geom": "geometry"}
    init_url_categories = {
        "sector": "outdoor_sector",
        "practice": "outdoor_practice",
        "scale": "outdoor_ratingscale",
        "ratings": "outdoor_rating",
        "type": "outdoor_coursetype",
    }
    url_categories = {
        "structure": "structure",
        "themes": "theme",
        "labels": "label",
        "source": "source",
        "managers": "organism",
    }
    categories_keys_api_v2 = {
        "structure": "name",
        "themes": "label",
        "type": "name",
        "labels": "name",
        "source": "name",
        "managers": "name",
    }
    natural_keys = {
        "structure": "name",
        "themes": "label",
        "type": "name",
        "labels": "name",
        "source": "name",
        "managers": "organism",
    }

    def start_meta(self):
        super().start_meta()
        self.parents_sites = {}
        self.children_courses = {}
        self.next_url = f"{self.url}/api/v2/outdoor_course"

    def filter_type(self, src, val):
        if val:
            type_id = self.get_id_from_mapping(
                self.field_options["type"]["mapping"], val
            )
            if type_id:
                return CourseType.objects.get(pk=type_id)
        return None

    def filter_points_reference(self, src, val):
        if val:
            return str(val)
        return None

    def start(self):
        super().start()
        self.init_outdoor_category("type", CourseType, join_field="practice")

    def parse_row(self, row):
        super().parse_row(row)
        self.children_courses[row["uuid"]] = row["children_uuids"]
        self.parents_sites[row["uuid"]] = row["sites_uuids"]

    def end(self):
        """Add children after all Sites and Courses imported are created in database."""
        for child, parents in self.parents_sites.items():
            child_course = Course.objects.get(eid=child)
            parents_ids = []
            for parent in parents:
                try:
                    parent_site = Site.objects.get(eid=parent)
                except Site.DoesNotExist:
                    self.add_warning(
                        f"Trying to retrieve missing parent Site (UUID: {parent}) for child Course (UUID: {child})"
                    )
                    continue
                parents_ids.append(parent_site.pk)
            child_course.parent_sites.set(parents_ids)

        """Add children after all Courses imported are created in database."""
        for parent, children in self.children_courses.items():
            parent_course = Course.objects.get(eid=parent)
            for i, child in enumerate(children):
                try:
                    child_course = Course.objects.get(eid=child)
                except Course.DoesNotExist:
                    self.add_warning(
                        f"Trying to retrieve missing child Course (UUID: {child}) for parent Course (UUID: {parent})"
                    )
                    continue
                OrderedCourseChild.objects.update_or_create(
                    parent=parent_course, child=child_course, defaults={"order": i}
                )
        super().end()


class OpenStreetMapOutdoorSiteParser(
    OpenStreetMapAttachmentsParserMixin, OpenStreetMapParser
):
    """Parser to import outdoor sites from OpenStreetMap"""

    url_polygons = "https://polygons.openstreetmap.fr/get_wkt.py"

    practice = None
    themes = None
    portal = None
    source = None
    model = Site
    eid = "eid"

    fields = {
        "eid": ("type", "id"),  # ids are unique only for object of the same type,
        "name": "tags.name",
        "description": "tags.description",
        "geom": ("type", "id", "lon", "lat", "geometry", "members"),
        "practice": "tags.leisure",
    }
    constant_fields = {}
    m2m_constant_fields = {}
    m2m_fields = {"web_links": ("tags.website", "tags.contact:website")}
    natural_keys = {
        "practice": "name",
        "themes": "label",
        "source": "name",
        "portal": "name",
        "web_links": "url",
    }
    field_options = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constant_fields = self.constant_fields.copy()
        self.m2m_constant_fields = self.m2m_constant_fields.copy()
        self.field_options = self.field_options.copy()
        if self.themes is not None:
            self.m2m_constant_fields["themes"] = self.themes
        if self.portal is not None:
            self.m2m_constant_fields["portal"] = self.portal
        if self.source is not None:
            self.m2m_constant_fields["source"] = self.source

    def way(self, geometry):
        coordinates = [[point["lon"], point["lat"]] for point in geometry]
        if coordinates[0] != coordinates[-1]:
            geom = LineString(coordinates, srid=self.osm_srid)
        else:
            geom = Polygon(coordinates)
        return geom

    def filter_geom(self, src, val):
        type, id, lng, lat, geometry, geometry_members = val
        geom_members = []
        if type == "node":
            geom = Point(float(lng), float(lat), srid=self.osm_srid)
            geom_members.append(geom)
        elif type == "way":
            geom_members.append(self.way(geometry))
        elif type == "relation":
            try:
                geom = self.get_polygon_from_API(id)

                if isinstance(geom, MultiPolygon):
                    # Multipolygon are not supported in the database
                    polygons_list = [polygon for polygon in geom]
                    geom_members = polygons_list
                else:
                    geom_members.append(geom)

            except Exception:
                for member in geometry_members:
                    if member["type"] == "node":
                        lng = member["lon"]
                        lat = member["lat"]
                        geom_members.append(
                            Point(float(lng), float(lat), srid=self.osm_srid)
                        )
                    elif member["type"] == "way":
                        geom_members.append(self.way(member["geometry"]))

        geom_collection = GeometryCollection(geom_members, srid=self.osm_srid)
        geom_collection.transform(settings.SRID)

        return geom_collection

    def filter_practice(self, src, val):
        if val == "sports_centre":
            msg = "This object is an indoor site."
            raise RowImportError(msg)

        practice = self.filter_fk(
            src, self.practice, Practice, self.natural_keys["practice"]
        )
        return practice

    def filter_web_links(self, src, val):
        url = next((item for item in val if item is not None), None)
        weblink = []
        if url:
            weblink.append(WebLink.objects.create(name=url, url=url))
        return weblink
