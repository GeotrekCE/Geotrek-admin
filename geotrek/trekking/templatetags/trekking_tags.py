import json

from django import template

from geotrek.trekking.models import Practice, RatingScale

register = template.Library()


@register.simple_tag
def trek_practices():
    practices = {
        str(practice.pk): {
            "scales": {
                str(scale.pk): scale.name for scale in practice.rating_scales.all()
            },
        }
        for practice in Practice.objects.prefetch_related("rating_scales").all()
    }
    return json.dumps(practices)


@register.simple_tag
def all_ratings_scales():
    scales = {str(scale.pk): scale.name for scale in RatingScale.objects.all()}
    return json.dumps(scales)
