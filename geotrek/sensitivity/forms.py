from django import forms
from .models import SensitiveArea, SportPractice, Species
from geotrek.common.forms import CommonForm
from django.utils.translation import ugettext as _


class SensitiveAreaForm(CommonForm):
    geomfields = ['geom']

    class Meta:
        fields = ['species', 'published', 'geom']
        model = SensitiveArea


class RegulatorySensitiveAreaForm(CommonForm):
    geomfields = ['geom']
    name = forms.CharField(max_length=250, label=_(u"Name"))
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
        fields = ['name', 'published', 'practices'] + ['period{:02}'.format(p) for p in range(1, 13)] + ['url', 'geom']
        model = SensitiveArea

    def __init__(self, *args, **kwargs):
        super(RegulatorySensitiveAreaForm, self).__init__(*args, **kwargs)
        self.helper.form_action += '?category=2'

    def save(self):
        if not self.instance.pk:
            self.instance.species = Species()
        self.instance.species.name = self.cleaned_data['name']
        self.instance.species.url = self.cleaned_data['url']
        for p in range(1, 13):
            fieldname = 'period{:02}'.format(p)
            setattr(self.instance.species, fieldname, self.cleaned_data[fieldname])
        self.instance.species.save()
        self.instance.species.practices = self.cleaned_data['practices']
        print(self.instance.species)
        print(self.instance.species.pk)
        print(self.instance.pk)
        return super(RegulatorySensitiveAreaForm, self).save()
