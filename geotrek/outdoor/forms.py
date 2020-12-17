from crispy_forms.layout import Div
from geotrek.common.forms import CommonForm
from geotrek.outdoor.models import Site


class SiteForm(CommonForm):
    geomfields = ['geom']

    fieldslayout = [
        Div(
            'structure',
            'name',
            'parent',
            'review',
            'published',
            'practice',
            'description',
            'description_teaser',
            'ambiance',
            'advice',
            'period',
            'labels',
            'themes',
            'portal',
            'source',
            'information_desks',
            'web_links',
            'type',
            'eid',
        )
    ]

    class Meta:
        fields = ['geom', 'structure', 'name', 'review', 'published', 'practice', 'description',
                  'description_teaser', 'ambiance', 'advice', 'period', 'labels', 'themes',
                  'portal', 'source', 'information_desks', 'web_links', 'type', 'parent', 'eid']
        model = Site
