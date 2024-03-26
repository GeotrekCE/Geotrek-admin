from django.conf import settings
from django.core import validators
from tinymce.widgets import TinyMCE

from treebeard.forms import MoveNodeForm

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from geotrek.common.models import Attachment, FileType
from geotrek.flatpages.models import FlatPage, MenuItem
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

    class Meta:
        model = MenuItem
        fields = (
            'title',
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

    class Media:

        js = ('flatpages/js/menu_item_fieldsets.js',)

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

    def clean(self):
        """Ensures that:
          - field `page` has a value if target_type is "page" and
          - field `link_url` (for the default language only) has a value if target_type is "link".

        It also erases values for fields not relevant to the target_type, for instance if target_type is "page"
        all `link_url` values are erased.
         """
        target_type = self.cleaned_data["target_type"]
        if target_type == "page":
            if self.cleaned_data["page"] is None:
                raise ValidationError({"page": "This field is required."})

        if target_type == "link":
            link_url_loc_fieldname = build_localized_fieldname("link_url", settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
            if (
                    link_url_loc_fieldname in self.cleaned_data
                    and self.cleaned_data[link_url_loc_fieldname] in validators.EMPTY_VALUES):
                raise ValidationError({link_url_loc_fieldname: "This field is required."})
