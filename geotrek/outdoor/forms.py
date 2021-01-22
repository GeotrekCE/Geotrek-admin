from crispy_forms.layout import Div
from django import forms
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
            'type',
            'description_teaser',
            'ambiance',
            'description',
            'advice',
            'period',
            'orientation',
            'wind',
            'labels',
            'themes',
            'information_desks',
            'web_links',
            'portal',
            'source',
            'eid',
        )
    ]

    class Meta:
        fields = ['geom', 'structure', 'name', 'review', 'published', 'practice', 'description',
                  'description_teaser', 'ambiance', 'advice', 'period', 'labels', 'themes',
                  'portal', 'source', 'information_desks', 'web_links', 'type', 'parent', 'eid',
                  'orientation', 'wind']
        model = Site

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['orientation'].widget = forms.SelectMultiple(choices=Site.ORIENTATION_CHOICES)
        self.fields['wind'].widget = forms.SelectMultiple(choices=Site.ORIENTATION_CHOICES)
        if self.instance.pk:
            descendants = self.instance.get_descendants(include_self=True).values_list('pk', flat=True)
            self.fields['parent'].queryset = Site.objects.exclude(pk__in=descendants)
        if self.instance.practice:
            for scale in self.instance.practice.rating_scales.all():
                for bound in ('max', 'min'):
                    ratings = getattr(self.instance, 'ratings_' + bound).filter(scale=scale)
                    fieldname = 'rating_scale_{}{}'.format(bound, scale.pk)
                    self.fields[fieldname] = forms.ModelChoiceField(
                        label="{} {}".format(scale.name, bound),
                        queryset=scale.ratings.all(),
                        required=False,
                        initial=ratings[0] if ratings else None
                    )
                    self.fieldslayout[0].insert(10, fieldname)

    def save(self, *args, **kwargs):
        site = super().save(self, *args, **kwargs)

        # Save ratings
        if site.practice:
            for bound in ('min', 'max'):
                field = getattr(site, 'ratings_' + bound)
                to_remove = list(field.exclude(scale__practice=site.practice).values_list('pk', flat=True))
                to_add = []
                for scale in site.practice.rating_scales.all():
                    rating = self.cleaned_data.get('rating_scale_{}{}'.format(bound, scale.pk))
                    if rating:
                        to_remove += list(field.filter(scale=scale).exclude(pk=rating.pk).values_list('pk', flat=True))
                        to_add.append(rating.pk)
                    else:
                        to_remove += list(field.filter(scale=scale).values_list('pk', flat=True))
                field.remove(*to_remove)
                field.add(*to_add)

        return site
