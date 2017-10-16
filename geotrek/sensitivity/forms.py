from django import forms
from .models import SensitiveArea, SportPractice, Species
from geotrek.common.forms import CommonForm
from django.utils.translation import ugettext as _


class SensitiveAreaForm(CommonForm):
    geomfields = ['geom']
    species = forms.ModelChoiceField(queryset=Species.objects.filter(category=Species.SPECIES))

    class Meta:
        fields = ['species', 'description', 'email', 'published', 'geom']
        model = SensitiveArea


class RegulatorySensitiveAreaForm(CommonForm):
    geomfields = ['geom']
    name = forms.CharField(max_length=250, label=_(u"Name"))
    pictogram = forms.FileField()
    period01 = forms.BooleanField(label=_(u"January"), required=False)
    period02 = forms.BooleanField(label=_(u"February"), required=False)
    period03 = forms.BooleanField(label=_(u"March"), required=False)
    period04 = forms.BooleanField(label=_(u"April"), required=False)
    period05 = forms.BooleanField(label=_(u"May"), required=False)
    period06 = forms.BooleanField(label=_(u"June"), required=False)
    period07 = forms.BooleanField(label=_(u"July"), required=False)
    period08 = forms.BooleanField(label=_(u"August"), required=False)
    period09 = forms.BooleanField(label=_(u"September"), required=False)
    period10 = forms.BooleanField(label=_(u"October"), required=False)
    period11 = forms.BooleanField(label=_(u"November"), required=False)
    period12 = forms.BooleanField(label=_(u"Decembre"), required=False)
    practices = forms.ModelMultipleChoiceField(label=_(u"Sport practices"), queryset=SportPractice.objects)
    url = forms.URLField(label="URL", required=False)

    class Meta:
        fields = ['name', 'published', 'pictogram', 'practices'] + ['period{:02}'.format(p) for p in range(1, 13)] + ['url', 'geom']
        model = SensitiveArea

    def __init__(self, *args, **kwargs):
        super(RegulatorySensitiveAreaForm, self).__init__(*args, **kwargs)
        self.helper.form_action += '?category=2'

    def save(self):
        if not self.instance.pk:
            species = Species()
        else:
            species = self.instance.species
        species.name = self.cleaned_data['name']
        species.url = self.cleaned_data['url']
        for p in range(1, 13):
            fieldname = 'period{:02}'.format(p)
            setattr(species, fieldname, self.cleaned_data[fieldname])
        species.category = Species.REGULATORY
        species.save()
        species.practices = self.cleaned_data['practices']
        area = super(RegulatorySensitiveAreaForm, self).save(commit=False)
        area.species = species
        area.save()
        return area
