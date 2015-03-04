from django.contrib import admin
from django.conf import settings

from modeltranslation.admin import TranslationAdmin
from tinymce.widgets import TinyMCE

from geotrek.flatpages import models as flatpages_models


class FlatPagesAdmin(TranslationAdmin):
    list_display = ('title', 'published', 'publication_date', 'target')
    search_fields = ('title', 'content')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name[:7] == 'content':
            return db_field.formfield(widget=TinyMCE)
        return super(FlatPagesAdmin, self).formfield_for_dbfield(db_field, **kwargs)


if settings.FLATPAGES_ENABLED:
    admin.site.register(flatpages_models.FlatPage, FlatPagesAdmin)
