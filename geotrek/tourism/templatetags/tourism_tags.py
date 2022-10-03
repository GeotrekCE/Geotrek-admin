import json

from django import template
from django.conf import settings
from django.contrib.gis.db.models.functions import Transform

from geotrek.tourism.models import TouristicContentCategory, TouristicEventPlace


register = template.Library()


@register.simple_tag
def touristic_content_categories():
    categories = {
        str(category.pk): {
            'type1_label': category.type1_label,
            'type2_label': category.type2_label,
            'type1_values': {
                str(type.pk): type.label
                for type in category.types.filter(in_list=1)
            },
            'type2_values': {
                str(type.pk): type.label
                for type in category.types.filter(in_list=2)
            },
            'geometry_type': category.geometry_type
        }
        for category in TouristicContentCategory.objects.all()
    }
    return json.dumps(categories)


@register.simple_tag
def is_tourism_enabled():
    return settings.TOURISM_ENABLED


@register.simple_tag
def places_coords():
    places = TouristicEventPlace.objects.annotate(
        geom_4326=Transform('geom', 4326)  # Leaflet requries 4326
    )
    return json.dumps({str(p.pk): p.geom_4326.coords for p in places})
