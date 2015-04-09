import floppyforms as forms

from django.utils.translation import ugettext_lazy as _

from geotrek.common.forms import CommonForm
from geotrek.flatpages.models import FlatPage


class FlatPageForm(CommonForm):
    content = forms.CharField(widget=forms.TextInput, label=_(u"Content"))

    class Meta:
        model = FlatPage
        fields = ('title', 'published', 'external_url', 'target', 'content')
