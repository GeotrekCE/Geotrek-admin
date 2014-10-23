from django.db import models
from django.contrib import admin

from leaflet.admin import LeafletGeoAdmin
from tinymce.widgets import TinyMCE
from modeltranslation.admin import TranslationAdmin

from geotrek.tourism import models as tourism_models


class DataSourceAdmin(TranslationAdmin):
    list_display = ('title', 'pictogram_img')
    search_fields = ('title',)

admin.site.register(tourism_models.DataSource, DataSourceAdmin)


class InformationDeskTypeAdmin(TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label', )

admin.site.register(tourism_models.InformationDeskType, InformationDeskTypeAdmin)


class InformationDeskAdmin(LeafletGeoAdmin, TranslationAdmin):
    list_display = ('name', 'website', 'municipality')
    search_fields = ('name',)

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE},
    }

admin.site.register(tourism_models.InformationDesk, InformationDeskAdmin)


class TouristicContentCategoryAdmin(TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label',)

admin.site.register(tourism_models.TouristicContentCategory, TouristicContentCategoryAdmin)


class TouristicContentTypeAdmin(TranslationAdmin):
    list_display = ('category', 'type_nr', 'label')
    list_display_links = ('label', )
    list_filter = ('type_nr', )
    search_fields = ('label', )
    ordering = ('category', 'type_nr', 'label')

admin.site.register(tourism_models.TouristicContentType, TouristicContentTypeAdmin)


class TouristicEventUsageAdmin(TranslationAdmin):
    search_fields = ('usage',)

admin.site.register(tourism_models.TouristicEventUsage, TouristicEventUsageAdmin)


class TouristicEventPublicAdmin(TranslationAdmin):
    search_fields = ('public',)

admin.site.register(tourism_models.TouristicEventPublic, TouristicEventPublicAdmin)
