import json

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from geotrek.tourism.models import TouristicContentCategory


register = template.Library()


@register.assignment_tag
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
        }
        for category in TouristicContentCategory.objects.all()
    }
    return json.dumps(categories)
