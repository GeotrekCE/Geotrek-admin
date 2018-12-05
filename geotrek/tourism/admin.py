from django.db import models
from django.conf import settings
from django.contrib import admin

from leaflet.admin import LeafletGeoAdmin
from tinymce.widgets import TinyMCE
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

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


class TouristicContentType1Inline(TranslationTabularInline):
    model = tourism_models.TouristicContentType1
    readonly_fields = ('in_list',)
    extra = 0


class TouristicContentType2Inline(TranslationTabularInline):
    model = tourism_models.TouristicContentType2
    readonly_fields = ('in_list',)
    extra = 0


class TouristicContentCategoryAdmin(TranslationAdmin):
    list_display = ('label', 'order', 'pictogram_img', 'type1_label', 'type2_label')
    search_fields = ('label',)
    inlines = [
        TouristicContentType1Inline,
        TouristicContentType2Inline,
    ]


if settings.TOURISM_ENABLED:
    admin.site.register(tourism_models.TouristicContentCategory, TouristicContentCategoryAdmin)


class TouristicEventTypeAdmin(TranslationAdmin):
    list_display = ('type', 'pictogram_img')
    search_fields = ('type',)


if settings.TOURISM_ENABLED:
    admin.site.register(tourism_models.TouristicEventType, TouristicEventTypeAdmin)


class ReservationSystemAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


if settings.TOURISM_ENABLED:
    admin.site.register(tourism_models.ReservationSystem, ReservationSystemAdmin)
