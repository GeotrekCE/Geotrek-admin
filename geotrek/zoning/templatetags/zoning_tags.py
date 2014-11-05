import json

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from geotrek.zoning.models import District, City, RestrictedArea, RestrictedAreaType


register = template.Library()


def get_bbox_cities():
    return [
        (unicode(city) or city.pk, city.geom.transform(settings.API_SRID, clone=True).extent)
        for city in City.objects.all()
    ]


def get_bbox_districts():
    return [
        (unicode(district) or district.pk, district.geom.transform(settings.API_SRID, clone=True).extent)
        for district in District.objects.all()
    ]


def get_bbox_areas():
    return [
        (unicode(area) or area.pk, area.geom.transform(settings.API_SRID, clone=True).extent)
        for area in RestrictedArea.objects.all()
    ]


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


@register.assignment_tag
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
