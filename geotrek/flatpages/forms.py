import floppyforms as forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from geotrek.common.forms import CommonForm
from geotrek.flatpages.models import FlatPage
from modeltranslation.settings import AVAILABLE_LANGUAGES


class FlatPageForm(CommonForm):
    content = forms.CharField(widget=forms.Textarea, label=_(u"Content"))

    def __init__(self, *args, **kwargs):
        super(FlatPageForm, self).__init__(*args, **kwargs)
        # Revert widget modifications done by MapentityForm.__init__()
        for fieldname in self.fields.keys():
            if fieldname.startswith('content_'):
                self.fields[fieldname].widget = forms.Textarea()
        self.fields['source'].help_text = None
        self.fields['portal'].help_text = None

    class Meta:
        model = FlatPage
        fields = (
            'title', 'order', 'published', 'source',
            'portal', 'external_url', 'target', 'content'
        )

    def clean(self):
        cleaned_data = super(FlatPageForm, self).clean()
        for lang in AVAILABLE_LANGUAGES:
            external_url = cleaned_data.get('external_url_' + lang, None)
            if external_url is not None and len(external_url) > 0:
                if 'content_' + lang in self.errors:
                    self.errors.pop('content_' + lang)

            # Test if HTML was filled
            # Use strip_tags() to catch empty tags (e.g. ``<p></p>``)
            html_content = cleaned_data.get('content_{}'.format(lang), None) or ''
            if external_url and external_url.strip() and strip_tags(html_content):
                raise ValidationError(_('Choose between external URL and HTML content'))

        return cleaned_data
