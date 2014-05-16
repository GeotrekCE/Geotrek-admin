from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from geotrek.tourism.models import DataSource


class DataSourceAdmin(TranslationAdmin):
    list_display = ('title', 'pictogram_img')
    search_fields = ('title',)


admin.site.register(DataSource, DataSourceAdmin)
