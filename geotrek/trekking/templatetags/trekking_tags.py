from django import template

import json
from geotrek.trekking.models import RatingScale


register = template.Library()


@register.simple_tag
def all_ratings_scales():
    scales = {
        str(scale.pk): scale.name
        for scale in RatingScale.objects.all()
    }
    return json.dumps(scales)
