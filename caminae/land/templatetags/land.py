from django import template
from django.conf import settings

from caminae.land.models import District, City, RestrictedArea

register = template.Library()


def get_bbox_cities():
    return [
        (city.name or city.pk, city.geom.transform(settings.API_SRID, clone=True).extent)
        for city in City.objects.all()
    ]

def get_bbox_districts():
    return [
        (district.name or district.pk, district.geom.transform(settings.API_SRID, clone=True).extent)
        for district in District.objects.all()
    ]

def get_bbox_areas():
    return [
        (area.name or area.pk, area.geom.transform(settings.API_SRID, clone=True).extent)
        for area in RestrictedArea.objects.all()
    ]

@register.inclusion_tag('land/bbox.html')
def combobox_bbox_land():
    return { 
        'bbox_cities': get_bbox_cities(), 
        'bbox_districts': get_bbox_districts(), 
        'bbox_areas': get_bbox_areas() 
    }
