from django.contrib import admin
from django.conf import settings
from django.utils.translation import gettext as _
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from geotrek.flatpages import models as flatpages_models
from geotrek.flatpages.forms import FlatPageForm

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin


class FlatPagesAdmin(TabbedTranslationAdmin, TreeAdmin):
    list_display = ('title', 'published', 'publication_date', 'portals', )
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


class MyListFilter(admin.filters.SimpleListFilter):

    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)

    def choices(self, changelist):
        for choice in super().choices(changelist):
            if choice["display"] != _('All'):
                yield choice


# class MenuItemAdmin(TabbedTranslationAdmin, TreeAdmin): # diamond inheritance problem
class MenuItemAdmin(TabbedTranslationAdmin, TreeAdmin):
    list_display = (
        'label',
        'portal_names_string',
    )
    form = movenodeform_factory(flatpages_models.MenuItem)
    list_filter = (
        ("portals", admin.filters.RelatedOnlyFieldListFilter),
    )


if settings.FLATPAGES_ENABLED:
    admin.site.register(flatpages_models.FlatPage, FlatPagesAdmin)
    admin.site.register(flatpages_models.MenuItem, MenuItemAdmin)
