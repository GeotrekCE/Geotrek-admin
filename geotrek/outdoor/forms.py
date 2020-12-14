from crispy_forms.layout import Div
from django import forms
from geotrek.common.forms import CommonForm
from geotrek.outdoor.models import Site, Practice, SitePractice


class SiteForm(CommonForm):
    practices = forms.ModelMultipleChoiceField(
        queryset=Practice.objects.all(),
        required=False
    )

    geomfields = ['geom']

    fieldslayout = [
        Div(
            'structure',
            'name',
            'practices',
            'description',
            'eid',
        )
    ]

    class Meta:
        fields = ['structure', 'name', 'description', 'geom', 'practices', 'eid']
        model = Site

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['practices'].initial = self.instance.site_practices.values_list('practice', flat=True)

    def save(self, commit=True):
        site = super().save(commit=commit)
        if commit:
            for practice in Practice.objects.all():
                if practice in self.cleaned_data['practices']:
                    SitePractice.objects.get_or_create(site=site, practice=practice)
                else:
                    SitePractice.objects.filter(site=site, practice=practice).delete()
            site.save()
        return site
