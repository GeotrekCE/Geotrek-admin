from django import template
from django.conf import settings

from geotrek.zoning.models import District, City, RestrictedArea


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
