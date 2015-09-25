import floppyforms as forms

from django.utils.translation import ugettext_lazy as _

from geotrek.common.forms import CommonForm
from geotrek.flatpages.models import FlatPage


class FlatPageForm(CommonForm):
    content = forms.CharField(widget=forms.TextInput, label=_(u"Content"))

    def __init__(self, *args, **kwargs):
        super(FlatPageForm, self).__init__(*args, **kwargs)
        self.fields['source'].help_text = None

    class Meta:
        model = FlatPage
        fields = ('title', 'published', 'source', 'external_url', 'target', 'content')
