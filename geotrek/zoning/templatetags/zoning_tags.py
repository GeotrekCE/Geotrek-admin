from django.db.models.query import Prefetch
import json

from django import template
from django.contrib.gis.db.models import Extent
from django.contrib.gis.db.models.functions import Envelope, Transform
from django.conf import settings
from django.db.models.functions import Coalesce
from django.urls import reverse

from geotrek.zoning.models import District, City, RestrictedArea, RestrictedAreaType


register = template.Library()


def get_bbox_cities():
    return City.objects.annotate(label=Coalesce("name", "code"), extent=Extent(Transform(Envelope('geom'), settings.API_SRID))).\
        values_list('label', 'extent').order_by('label')


def get_bbox_districts():
    return District.objects.annotate(extent=Extent(Transform(Envelope('geom'), settings.API_SRID))).\
        values_list('name', 'extent').order_by('name')


def get_bbox_areas():
    return RestrictedArea.objects.annotate(extent=Extent(Transform(Envelope('geom'), settings.API_SRID))).\
        values_list('name', 'extent').order_by('name')


@register.inclusion_tag('zoning/_bbox_fragment.html')
def combobox_bbox_land():
    cities = get_bbox_cities() if settings.LAND_BBOX_CITIES_ENABLED else []
    districts = get_bbox_districts() if settings.LAND_BBOX_DISTRICTS_ENABLED else []
    areas = get_bbox_areas() if settings.LAND_BBOX_AREAS_ENABLED else []
    return {
        'bbox_cities': cities,
        'bbox_districts': districts,
        'bbox_areas': areas
    }


@register.simple_tag
def restricted_area_types():
    all_used_types = RestrictedArea.objects.values_list('area_type', flat=True)
    used_types = RestrictedAreaType.objects.filter(pk__in=all_used_types)
    serialized = []
    for area_type in used_types:
        area_type_url = reverse('zoning:restrictedarea_type_layer',
                                kwargs={'type_pk': area_type.pk})
        serialized.append({
            'id': 'restrictedarea',
            'name': area_type.name,
            'url': area_type_url
        })
    return json.dumps(serialized)


@register.simple_tag
def restricted_areas_by_type():
    restricted_areas_by_type = {
        str(type.pk): {
            'areas': [{
                str(area.pk): type.name + " - " + area.name
            } for area in type.restrictedarea_set.all()
            ]  # We use an array instead of dict because JS parsing would re-order JSON dict
        }
        for type in RestrictedAreaType.objects.all().prefetch_related(
            Prefetch('restrictedarea_set', queryset=RestrictedArea.objects.order_by('name')))
    }
    return json.dumps(restricted_areas_by_type)


@register.simple_tag
def all_restricted_areas():
    all_restricted_areas = [{
        str(area.pk): area.area_type.name + " - " + area.name
    } for area in RestrictedArea.objects.select_related('area_type').order_by('area_type__name', 'name')
    ]  # We use an array instead of dict because JS parsing would re-order JSON dict
    return json.dumps(all_restricted_areas)
