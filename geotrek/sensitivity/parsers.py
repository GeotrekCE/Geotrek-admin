# -*- encoding: utf-8 -*-

import requests

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.utils.translation import ugettext as _

from geotrek.common.parsers import Parser, ShapeParser, GlobalImportError
from .models import SensitiveArea, Species, SportPractice


class BiodivParser(Parser):
    model = SensitiveArea
    label = "Biodiv'Sports"
    url = 'http://biodiv-sports.fr/api/v2/sensitivearea/?format=json&period=ignore'
    eid = 'eid'
    separator = None
    delete = True
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
        response = requests.get(self.url)
        if response.status_code != 200:
            msg = _(u"Failed to download {url}. HTTP status code {status_code}")
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
        geom = Polygon(val['coordinates'][0], srid=4326)  # WGS84
        geom.transform(settings.SRID)
        return geom

    def filter_species(self, src, val):
        (eid, names, period, practice_names, url) = val
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
            if translation != getattr(species, 'name_' + lang):
                setattr(species, 'name_' + lang, translation)
                need_save = True
        for i in range(12):
            if period[i] != getattr(species, 'period{:02}'.format(i + 1)):
                setattr(species, 'period{:02}'.format(i + 1), period[i])
                need_save = True
        practices = [SportPractice.objects.get_or_create(name=name)[0] for name in practice_names]
        if url != species.url:
            species.url = url
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
    label = u"Shapefile zone sensible espèce"
    separator = ','
    delete = False
    fields = {
        'geom': 'geom',
        'contact': 'contact',
        'species': 'espece',
    }
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    natural_keys = {
        'species': 'name',
    }
    field_options = {
        'species': {'required': True}
    }
