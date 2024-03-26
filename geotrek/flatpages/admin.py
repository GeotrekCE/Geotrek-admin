from django.contrib import admin
from django.conf import settings
from django.utils.translation import gettext as _
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from geotrek.flatpages import models as flatpages_models
from geotrek.flatpages.forms import FlatPageForm, MenuItemForm


if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin


class FlatPagesAdmin(TabbedTranslationAdmin, TreeAdmin):
    list_display = ('title', 'published', 'publication_date', 'portal_names_string', )
    list_filter = ('published', )
    search_fields = ('title', 'content')
    form = movenodeform_factory(flatpages_models.FlatPage, form=FlatPageForm)

    # This is an alternative to overriding super(TabbedTranslationAdmin)._get_declared_fields
    # Manual specification of fields to display treebeard's `_position` and `_ref_node_id` field.
    # fields = (
    #     'title',
    #     'published',
    #     'portals',
    #     'content',
    #     '_position',
    #     '_ref_node_id',
    # )

    def portals(self, obj):
        return ', '.join([portal.name for portal in obj.portal.all()])
    portals.short_description = _("Portals")

    # Override modeltranslation's TranslationAdmin._get_declared_fieldsets
    # The original method does not preserve MoveNodeForm's declared FormFields (aka class attributes) when
    # dynamically creating a Form class for the Admin add and change views.
    def _get_declared_fieldsets(self, request, obj=None):
        # Take custom modelform fields option into account
        # mdu : use self.form.base_fields rather than self.form._meta.fields
        # The latter does not have the FormFields declared as class attributes, hence breaking MoveNodeForm.
        if not self.fields and hasattr(self.form, 'base_fields') and self.form.base_fields:
            self.fields = self.form.base_fields.keys()

        # takes into account non-standard add_fieldsets attribute used by UserAdmin
        fieldsets = (
            self.add_fieldsets
            if getattr(self, 'add_fieldsets', None) and obj is None
            else self.fieldsets
        )
        if fieldsets:
            return self._patch_fieldsets(fieldsets)
        elif self.fields:
            return [(None, {'fields': self.replace_orig_field(self.get_fields(request, obj))})]
        return None

    def get_form(self, request, *args, **kwargs):
        # Django's ModelAdmin generates a ModelForm class based on FlatPageForm in the add/edit views. This override
        # injects the `user` attribute needed by FlatPageForm on the newly created Form class.
        form_class = super().get_form(request, *args, **kwargs)
        form_class.user = request.user
        return form_class

    def save_related(self, request, form, formsets, change):
        # Django's ModelAdmin first saves the form instance without commit awaiting for formsets' validations. We
        # perform the cover image save/update/deletion on `save_related` because we need the committed instance
        # (with an ID).
        super().save_related(request, form, formsets, change)
        form.save_cover_image()


class MyListFilter(admin.filters.SimpleListFilter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def choices(self, changelist):
        for choice in super().choices(changelist):
            if choice["display"] != _('All'):
                yield choice


class MenuItemAdmin(TabbedTranslationAdmin, TreeAdmin):
    # FIXME: there is a lot of duplicated code in this class and a need for another baseclass
    # It will be easier to refactor when the tests are ready.

    fieldsets = [
        (None, {
            'fields': [
                'label',
                'pictogram',
                'thumbnail',
                'portals',
                'platform',
                'published',
                'target_type',
            ],
        }),
        ('Page', {
            'fields': [
                'page',
            ],
            'classes': ('hidden', 'page_fieldset', )
        }),
        ('Link', {
            'fields': [
                'link_url',
                'open_in_new_tab',
            ],
            'classes': ('hidden', 'link_fieldset', )
        }),
        (None, {
            'fields': [
                '_position',
                '_ref_node_id',
            ],
        }),
    ]
    list_display = (
        'label',
        'portal_names_string',
    )
    form = movenodeform_factory(flatpages_models.MenuItem, form=MenuItemForm)
    list_filter = (
        ("portals", admin.filters.RelatedOnlyFieldListFilter),
    )

    # Override modeltranslation's TranslationAdmin._get_declared_fieldsets
    # The original method does not preserve MoveNodeForm's declared FormFields (aka class attributes) when
    # dynamically creating a Form class for the Admin add and change views.
    def _get_declared_fieldsets(self, request, obj=None):
        # Take custom modelform fields option into account
        # mdu : use self.form.base_fields rather than self.form._meta.fields
        # The latter does not have the FormFields declared as class attributes, hence breaking MoveNodeForm.
        if not self.fields and hasattr(self.form, 'base_fields') and self.form.base_fields:
            self.fields = self.form.base_fields.keys()

        # takes into account non-standard add_fieldsets attribute used by UserAdmin
        fieldsets = (
            self.add_fieldsets
            if getattr(self, 'add_fieldsets', None) and obj is None
            else self.fieldsets
        )
        if fieldsets:
            return self._patch_fieldsets(fieldsets)
        elif self.fields:
            return [(None, {'fields': self.replace_orig_field(self.get_fields(request, obj))})]
        return None

    def get_form(self, request, *args, **kwargs):
        # Django's ModelAdmin generates a ModelForm class based on FlatPageForm in the add/edit views. This override
        # injects the `user` attribute needed by FlatPageForm on the newly created Form class.
        form_class = super().get_form(request, *args, **kwargs)
        form_class.user = request.user
        return form_class

    def save_related(self, request, form, formsets, change):
        # Django's ModelAdmin first saves the form instance without commit awaiting for formsets' validations. We
        # perform the cover image save/update/deletion on `save_related` because we need the committed instance
        # (with an ID).
        super().save_related(request, form, formsets, change)
        form.save_thumbnail()


if settings.FLATPAGES_ENABLED:
    admin.site.register(flatpages_models.FlatPage, FlatPagesAdmin)
    admin.site.register(flatpages_models.MenuItem, MenuItemAdmin)
