from django.db import models
from django.conf import settings
from django.contrib import admin

from leaflet.admin import LeafletGeoAdmin
from tinymce.widgets import TinyMCE

from geotrek.common.mixins import MergeActionMixin
from geotrek.tourism import models as tourism_models

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
else:
    TranslationAdmin = admin.ModelAdmin
    TranslationTabularInline = admin.TabularInline


class InformationDeskTypeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label', )
    merge_field = 'label'


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


class TouristicContentCategoryAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('label', 'prefixed_id', 'order', 'pictogram_img', 'type1_label', 'type2_label')
    search_fields = ('label',)
    inlines = [
        TouristicContentType1Inline,
        TouristicContentType2Inline,
    ]
    merge_field = 'label'


if settings.TOURISM_ENABLED:
    admin.site.register(tourism_models.TouristicContentCategory, TouristicContentCategoryAdmin)


class TouristicEventTypeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('type', 'pictogram_img')
    search_fields = ('type',)
    merge_field = 'type'


if settings.TOURISM_ENABLED:
    admin.site.register(tourism_models.TouristicEventType, TouristicEventTypeAdmin)
