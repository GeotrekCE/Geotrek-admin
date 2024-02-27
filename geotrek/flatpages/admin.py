from django.contrib import admin
from django.conf import settings
from django.utils.translation import gettext as _
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from geotrek.flatpages import models as flatpages_models
from geotrek.flatpages.views import FlatPageCreate, FlatPageUpdate, MenuItemCreate

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin


from tinymce.widgets import TinyMCE, AdminTinyMCE
from django.forms import ModelForm
from django import forms

class FlatPagesAdminForm(ModelForm):

    content_fr = forms.CharField(widget=TinyMCE(attrs={"class": "vLargeTextField mt mt-field-content-fr mt-default"}))
    content_en = forms.CharField(widget=TinyMCE(attrs={"class": "vLargeTextField mt mt-field-content-fr mt-default"}))
    content_es = forms.CharField(widget=TinyMCE(attrs={"class": "vLargeTextField mt mt-field-content-fr mt-default"}))
    content_it = forms.CharField(widget=TinyMCE(attrs={"class": "vLargeTextField mt mt-field-content-fr mt-default"}))


# class FlatPagesAdmin(TabbedTranslationAdmin):
class FlatPagesAdmin(TreeAdmin):
    list_display = ('title', 'published', 'publication_date', 'portals', )
    list_filter = ('published', )
    search_fields = ('title', 'content')
    form = movenodeform_factory(flatpages_models.MenuItem)
    # form = FlatPagesAdminForm

    # def add_view(self, request, form_url='', extra_context=None):
    #     return FlatPageCreate.as_view()(request)
    #
    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     return FlatPageUpdate.as_view()(request, pk=object_id)

    def portals(self, obj):
        return ', '.join([portal.name for portal in obj.portal.all()])
    portals.short_description = _("Portals")


class MyListFilter(admin.filters.SimpleListFilter):

    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)

    def choices(self, changelist):
        for choice in super().choices(changelist):
            if choice["display"] != _('All'):
                yield choice


# class MenuItemAdmin(TabbedTranslationAdmin, TreeAdmin): # diamond inheritance problem
class MenuItemAdmin(TreeAdmin):
    list_display = ('label', )
    form = movenodeform_factory(flatpages_models.MenuItem)
    # change_form_template = "flatpages/change_form.html"
    list_filter = (
        ("portals", admin.filters.RelatedOnlyFieldListFilter),
    )


if settings.FLATPAGES_ENABLED:
    admin.site.register(flatpages_models.FlatPage, FlatPagesAdmin)
    admin.site.register(flatpages_models.MenuItem, MenuItemAdmin)
