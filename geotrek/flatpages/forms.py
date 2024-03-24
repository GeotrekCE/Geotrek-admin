from tinymce.widgets import TinyMCE

from treebeard.forms import MoveNodeForm

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from geotrek.common.models import Attachment, FileType
from geotrek.flatpages.models import FlatPage, MenuItem
from modeltranslation.settings import AVAILABLE_LANGUAGES
from modeltranslation.utils import build_localized_fieldname


class FlatPageForm(MoveNodeForm):
    cover_image = forms.ImageField(label=_("Cover image"), required=False)
    cover_image_author = forms.CharField(label=_("Cover image author"), max_length=128, required=False)

    user = None  # Set by .admin.FlatPagesAdmin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Content translation fields' widgets are replaced with the TinyMCE widget, original widget attrs
        # are passed along as they contain modeltranslation CSS classes.
        for fieldname, formfield in self.fields.items():
            if fieldname.startswith('content_'):
                self.fields[fieldname].widget = TinyMCE(attrs=self.fields[fieldname].widget.attrs)

        # self.fields['source'].help_text = None
        # self.fields['portal'].help_text = None

        if self.instance.pk:
            page = Attachment.objects.filter(
                content_type=ContentType.objects.get_for_model(FlatPage),
                object_id=self.instance.pk
            ).first()
            if page:
                self.fields['cover_image'].initial = page.attachment_file
                self.fields['cover_image_author'].initial = page.author

    class Meta:
        model = FlatPage
        fields = (
            'title',
            'published',
            'source',
            'portals',
            'cover_image',
            'cover_image_author',
            'content',
        )

    def clean(self):
        cleaned_data = super().clean()
        for lang in AVAILABLE_LANGUAGES:
            external_url = cleaned_data.get('external_url_' + lang, None)
            if external_url is not None and len(external_url) > 0:
                if 'content_' + lang in self.errors:
                    self.errors.pop('content_' + lang)

            # Test if HTML was filled
            # Use strip_tags() to catch empty tags (e.g. ``<p></p>``)
            html_content = cleaned_data.get(build_localized_fieldname('content', lang), None) or ''
            if external_url and external_url.strip() and strip_tags(html_content):
                raise ValidationError(_('Choose between external URL and HTML content'))

        return cleaned_data

    def save_cover_image(self):
        page = self.instance
        if self.cleaned_data['cover_image']:
            Attachment.objects.update_or_create(
                content_type=ContentType.objects.get_for_model(FlatPage),
                object_id=page.id,
                defaults={
                    'attachment_file': self.cleaned_data['cover_image'],
                    'filetype': FileType.objects.get_or_create(type="Photographie", structure=None)[0],
                    'creator': self.user,
                    'author': self.cleaned_data['cover_image_author'],
                    'starred': True,
                }
            )
        if not self.cleaned_data['cover_image']:
            Attachment.objects.filter(
                content_type=ContentType.objects.get_for_model(FlatPage),
                object_id=page.id,
            ).delete()
        return page


class MenuItemForm(MoveNodeForm):

    thumbnail = forms.ImageField(label=_("Thumbnail"), required=False)

    user = None  # Set by .admin.MenuItemAdmin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            page = Attachment.objects.filter(
                content_type=ContentType.objects.get_for_model(MenuItem),
                object_id=self.instance.pk
            ).first()
            if page:
                self.fields['thumbnail'].initial = page.attachment_file

        self.fields["link_url_fr"].required = True

    class Meta:
        model = MenuItem
        fields = (
            'label',
            'pictogram',
            'thumbnail',
            'published',
            'portals',
            'platform',
            'target_type',
            'page',
            'link_url',
            'open_in_new_tab',
        )

    def full_clean(self, *args, **kwargs):
        self.fields["link_url_fr"].required = False
        super().full_clean(*args, **kwargs)

    def save_thumbnail(self):
        page = self.instance
        if self.cleaned_data['thumbnail']:
            Attachment.objects.update_or_create(
                content_type=ContentType.objects.get_for_model(MenuItem),
                object_id=page.id,
                defaults={
                    'attachment_file': self.cleaned_data['thumbnail'],
                    'filetype': FileType.objects.get_or_create(type="Photographie", structure=None)[0],
                    'creator': self.user,
                }
            )
        if not self.cleaned_data['thumbnail']:
            Attachment.objects.filter(
                content_type=ContentType.objects.get_for_model(MenuItem),
                object_id=page.id,
            ).delete()
        return page
