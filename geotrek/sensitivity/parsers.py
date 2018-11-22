# -*- encoding: utf-8 -*-

import requests
import unicodedata

from django.conf import settings
from django.contrib.gis.geos import Point, Polygon
from django.utils.translation import ugettext as _

from geotrek.common.parsers import Parser, ShapeParser, GlobalImportError, RowImportError
from .models import SensitiveArea, Species, SportPractice


class BiodivParser(Parser):
    model = SensitiveArea
    label = "Biodiv'Sports"
    url = 'https://biodiv-sports.fr/api/v2/sensitivearea/?format=json&bubble&period=ignore'
    eid = 'eid'
    separator = None
    delete = True
    practices = None
    fields = {
        'eid': 'id',
        'geom': 'geometry',
        'contact': 'contact',
        'species': (
            'species_id',
            'name',
            'period',
            'practices',
            'info_url',
            'radius',
        )
    }
    constant_fields = {
        'published': True,
        'deleted': False,
    }

    def __init__(self, *args, **kwargs):
        super(BiodivParser, self).__init__(*args, **kwargs)
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            self.fields['description_' + lang] = 'description.' + lang

    @property
    def items(self):
        return self.root['results']

    def get_to_delete_kwargs(self):
        kwargs = super(BiodivParser, self).get_to_delete_kwargs()
        kwargs['eid__isnull'] = False
        return kwargs

    def next_row(self):
        response = requests.get('https://biodiv-sports.fr/api/v2/sportpractice/')
        if response.status_code != 200:
            msg = _("Failed to download https://biodiv-sports.fr/api/v2/sportpractice/. HTTP status code {status_code}")
            raise GlobalImportError(msg.format(url=response.url, status_code=response.status_code))
        for practice in response.json()['results']:
            defaults = {'name_' + lang: practice['name'][lang] for lang in practice['name'].keys() if lang in settings.MODELTRANSLATION_LANGUAGES}
            SportPractice.objects.get_or_create(id=practice['id'], defaults=defaults)
        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        bbox.transform(4326)  # WGS84
        url = self.url
        url += '&in_bbox={}'.format(','.join([str(coord) for coord in bbox.extent]))
        if self.practices:
            url += '&practices={}'.format(','.join([str(practice) for practice in self.practices]))
        response = requests.get(url)
        if response.status_code != 200:
            msg = _("Failed to download {url}. HTTP status code {status_code}")
            raise GlobalImportError(msg.format(url=response.url, status_code=response.status_code))

        self.root = response.json()
        self.nb = int(self.root['count'])

        for row in self.items:
            yield row

    def normalize_field_name(self, name):
        return name

    def filter_eid(self, src, val):
        return str(val)

    def filter_geom(self, src, val):
        if val['type'] == "Point":
            geom = Point(val['coordinates'], srid=4326)  # WGS84
        else:
            geom = Polygon(val['coordinates'][0], srid=4326)  # WGS84
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
        for lang, translation in list(names.items()):
            if lang in settings.MODELTRANSLATION_LANGUAGES and translation != getattr(species, 'name_' + lang):
                setattr(species, 'name_' + lang, translation)
                need_save = True
        for i in range(12):
            if period[i] != getattr(species, 'period{:02}'.format(i + 1)):
                setattr(species, 'period{:02}'.format(i + 1), period[i])
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


for i in range(12):
    def filter_period(self, src, val):
        return val[i]
    setattr(BiodivParser, 'filter_period{:02}'.format(i + 1), filter_period)


class SpeciesSensitiveAreaShapeParser(ShapeParser):
    model = SensitiveArea
    label = "Shapefile zone sensible espèce"
    separator = ','
    delete = False
    fields = {
        'geom': 'geom',
        'contact': 'contact',
        'description': 'description',
        'species': 'espece',
    }
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    field_options = {
        'species': {'required': True}
    }

    def filter_species(self, src, val):
        try:
            species = Species.objects.get(category=Species.SPECIES, name=val)
        except Species.DoesNotExist:
            msg = "L'espèce {} n'existe pas dans Geotrek. Merci de la créer.".format(val)
            raise RowImportError(msg)
        return species


class RegulatorySensitiveAreaShapeParser(ShapeParser):
    model = SensitiveArea
    label = "Shapefile zone sensible réglementaire"
    separator = ','
    delete = False
    fields = {
        'geom': 'geom',
        'contact': 'contact',
        'description': 'description',
        'species': (
            'nom',
            'periode',
            'pratiques',
            'url',
        )
    }
    constant_fields = {
        'published': True,
        'deleted': False,
    }

    def filter_species(self, src, val):
        (name, period, practice_names, url) = val
        species = Species(category=Species.REGULATORY)
        species.name = name
        if period:
            period = period.split(self.separator)
            for i in range(1, 13):
                if str(i) in period:
                    setattr(species, 'period{:02}'.format(i), True)
        species.url = url
        practices = []
        if practice_names:
            for practice_name in practice_names.split(self.separator):
                try:
                    practice = SportPractice.objects.get(name=practice_name)
                except SportPractice.DoesNotExist:
                    msg = "La pratique sportive {} n'existe pas dans Geotrek. Merci de l'ajouter.".format(practice_name)
                    raise RowImportError(msg)
                practices.append(practice)
        species.save()
        species.practices.add(*practices)
        return species

    def normalize_field_name(self, name):
        return unicodedata.normalize('NFD', str(name)).encode('ascii', 'ignore').upper()
