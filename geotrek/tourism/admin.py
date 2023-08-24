from django.db import models
from django.conf import settings
from django.contrib import admin

from leaflet.admin import LeafletGeoAdmin
from tinymce.widgets import TinyMCE

from geotrek.common.mixins.actions import MergeActionMixin
from geotrek.tourism import models as tourism_models

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin, TabularInline as TranslationTabularInline


class LabelAccessibilityAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label', )
    merge_field = 'label'


admin.site.register(tourism_models.LabelAccessibility, LabelAccessibilityAdmin)


class InformationDeskTypeAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label', )
    merge_field = 'label'


admin.site.register(tourism_models.InformationDeskType, InformationDeskTypeAdmin)


class InformationDeskAdmin(LeafletGeoAdmin, TabbedTranslationAdmin):
    list_display = ('name', 'website', 'municipality')
    search_fields = ('name',)

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE},
    }


admin.site.register(tourism_models.InformationDesk, InformationDeskAdmin)


class TouristicContentType1Inline(TranslationTabularInline):
    model = tourism_models.TouristicContentType1
    readonly_fields = ('in_list',)
    extra = 1


class TouristicContentType2Inline(TranslationTabularInline):
    model = tourism_models.TouristicContentType2
    readonly_fields = ('in_list',)
    extra = 1


class TouristicContentCategoryAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('label', 'prefixed_id', 'order', 'pictogram_img', 'type1_label', 'type2_label')
    search_fields = ('label',)
    inlines = [
        TouristicContentType1Inline,
        TouristicContentType2Inline,
    ]
    merge_field = 'label'


class TouristicEventTypeAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('type', 'pictogram_img')
    search_fields = ('type',)
    merge_field = 'type'


class TouristicEventParticipantCategoryAdmin(admin.ModelAdmin):
    list_display = ('label', 'order')


class CancellationReasonAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('label',)
    search_fields = ('label',)
    merge_field = 'label'


class TouristicEventPlaceAdmin(LeafletGeoAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


class TouristicEventOrganizerAdmin(admin.ModelAdmin):
    list_display = ('label',)
    list_filter = ('label',)
    search_fields = ('label',)


if settings.TOURISM_ENABLED:
    admin.site.register(tourism_models.TouristicContentCategory, TouristicContentCategoryAdmin)
    admin.site.register(tourism_models.TouristicEventType, TouristicEventTypeAdmin)
    admin.site.register(tourism_models.TouristicEventParticipantCategory, TouristicEventParticipantCategoryAdmin)
    admin.site.register(tourism_models.CancellationReason, CancellationReasonAdmin)
    admin.site.register(tourism_models.TouristicEventPlace, TouristicEventPlaceAdmin)
    admin.site.register(tourism_models.TouristicEventOrganizer, TouristicEventOrganizerAdmin)
