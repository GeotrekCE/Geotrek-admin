from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Point, Polygon

from geotrek.common.parsers import Parser, RowImportError, ShapeParser, ValueImportError

from .models import SensitiveArea, Species, SportPractice


class BiodivParser(Parser):
    model = SensitiveArea
    label = "Biodiv'Sports"
    url = "https://biodiv-sports.fr/api/v2/sensitivearea/?format=json&bubble&period=ignore"
    eid = "eid"
    separator = None
    delete = True
    practices = None
    next_url = ""
    fields = {
        "eid": "id",
        "geom": "geometry",
        "contact": "contact",
        "species": (
            "species_id",
            "name",
            "period",
            "practices",
            "info_url",
            "radius",
        ),
    }
    constant_fields = {
        "published": True,
        "deleted": False,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            self.fields["description_" + lang] = "description." + lang

    @property
    def items(self):
        return self.root["results"]

    def get_to_delete_kwargs(self):
        kwargs = super().get_to_delete_kwargs()
        kwargs["eid__isnull"] = False
        return kwargs

    def next_row(self):
        response = self.request_or_retry(
            "https://biodiv-sports.fr/api/v2/sportpractice/"
        )
        for practice in response.json()["results"]:
            defaults = {
                "name_" + lang: practice["name"][lang]
                for lang in practice["name"].keys()
                if lang in settings.MODELTRANSLATION_LANGUAGES
            }
            SportPractice.objects.get_or_create(id=practice["id"], defaults=defaults)
        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        bbox.transform(4326)  # WGS84
        self.next_url = self.url
        while self.next_url:
            params = {
                "in_bbox": ",".join([str(coord) for coord in bbox.extent]),
            }
            if self.practices:
                params["practices"] = ",".join(
                    [str(practice) for practice in self.practices]
                )
            response = self.request_or_retry(self.next_url, params=params)

            self.root = response.json()
            self.nb = int(self.root["count"])

            for row in self.items:
                yield row
            self.next_url = self.root["next"]

    def normalize_field_name(self, name):
        return name

    def filter_eid(self, src, val):
        return str(val)

    def filter_geom(self, src, val):
        if val["type"] == "Point":
            geom = Point(val["coordinates"], srid=4326)  # WGS84
        elif val["type"] == "Polygon":
            geom = Polygon(*val["coordinates"], srid=4326)  # WGS84
        elif val["type"] == "MultiPolygon":
            polygons = []
            for polygon in val["coordinates"]:
                polygons.append(Polygon(*polygon, srid=4326))
            geom = MultiPolygon(polygons, srid=4326)
        else:
            raise ValueImportError(
                "This object is neither a point, nor a polygon, nor a multipolygon"
            )
        geom.transform(settings.SRID)
        return geom

    def filter_species(self, src, val):
        (eid, names, period, practice_ids, url, radius) = val
        need_save = False
        if eid is None:  # Regulatory area
            try:
                species = self.obj.species
            except Species.DoesNotExist:
                species = Species(category=Species.REGULATORY)
        else:  # Species area
            try:
                species = Species.objects.get(eid=eid)
            except Species.DoesNotExist:
                species = Species(category=Species.SPECIES, eid=eid)
        for lang, translation in names.items():
            if lang in settings.MODELTRANSLATION_LANGUAGES and translation != getattr(
                species, "name_" + lang
            ):
                setattr(species, "name_" + lang, translation)
                need_save = True
        for i in range(12):
            if period[i] != getattr(species, f"period{i + 1:02}"):
                setattr(species, f"period{i + 1:02}", period[i])
                need_save = True
        practices = [SportPractice.objects.get(id=id) for id in practice_ids]
        if url != species.url:
            species.url = url
            need_save = True
        if radius != species.radius:
            species.radius = radius
            need_save = True
        if need_save:
            species.save()
        if set(practices) != set(species.practices.all()):
            species.practices.add(*practices)
        return species


class SpeciesSensitiveAreaShapeParser(ShapeParser):
    model = SensitiveArea
    label = "Shapefile zone sensible espèce"
    label_fr = "Shapefile zone sensible espèce"
    label_en = "Shapefile species sensitive area"
    separator = ","
    delete = False
    fields = {
        "geom": "geom",
        "contact": "contact",
        "description": "description",
        "species": "espece",
    }
    constant_fields = {
        "published": True,
        "deleted": False,
    }
    field_options = {"species": {"required": True}}

    def filter_species(self, src, val):
        try:
            species = Species.objects.get(category=Species.SPECIES, name=val)
        except Species.DoesNotExist:
            msg = f"L'espèce {val} n'existe pas dans Geotrek. Merci de la créer."
            raise RowImportError(msg)
        return species


class RegulatorySensitiveAreaShapeParser(ShapeParser):
    model = SensitiveArea
    label = "Shapefile zone sensible réglementaire"
    label_fr = "Shapefile zone sensible réglementaire"
    label_en = "Shapefile species sensitive area"
    separator = ","
    delete = False
    fields = {
        "geom": "geom",
        "contact": "contact",
        "description": "descriptio",
        "species": (
            "nom",
            "altitude",
            "periode",
            "pratiques",
            "url",
        ),
    }
    constant_fields = {
        "published": True,
        "deleted": False,
    }

    def filter_species(self, src, val):
        (name, elevation, period, practice_names, url) = val
        species = Species(category=Species.REGULATORY)
        species.name = name
        if period:
            period = period.split(self.separator)
            for i in range(1, 13):
                if str(i) in period:
                    setattr(species, f"period{i:02}", True)
        species.url = url
        species.radius = elevation
        practices = []
        if practice_names:
            for practice_name in practice_names.split(self.separator):
                try:
                    practice = SportPractice.objects.get(name=practice_name)
                except SportPractice.DoesNotExist:
                    msg = f"La pratique sportive {practice_name} n'existe pas dans Geotrek. Merci de l'ajouter."
                    raise RowImportError(msg)
                practices.append(practice)
        species.save()
        species.practices.add(*practices)
        return species
