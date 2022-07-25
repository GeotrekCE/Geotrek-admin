from django import template

import json
from geotrek.trekking.models import Practice, RatingScale


register = template.Library()


@register.simple_tag
def trek_practices():
    practices = {
        str(practice.pk): {
            'scales': {
                str(scale.pk): scale.name
                for scale in practice.rating_scales.all()
            },
        }
        for practice in Practice.objects.all().prefetch_related('rating_scales')
    }
    return json.dumps(practices)


@register.simple_tag
def all_ratings_scales():
    scales = {
        str(scale.pk): scale.name
        for scale in RatingScale.objects.all()
    }
    return json.dumps(scales)
