# -*- coding: utf-8 -*-


from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    POIType, Theme, TrekNetwork, Usage, Route, DifficultyLevel, WebLink, WebLinkCategory
)


class POITypeAdmin(TranslationAdmin):
    list_display = ('label',)
    search_fields = ('label',)


class ThemeAdmin(TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label',)


class TrekNetworkAdmin(TranslationAdmin):
    list_display = ('network',)
    search_fields = ('network',)


class UsageAdmin(TranslationAdmin):
    list_display = ('usage', 'pictogram_img')
    search_fields = ('usage',)


class RouteAdmin(TranslationAdmin):
    list_display = ('route',)
    search_fields = ('route',)


class DifficultyLevelAdmin(TranslationAdmin):
    list_display = ('difficulty',)
    search_fields = ('difficulty',)


class WebLinkAdmin(TranslationAdmin):
    list_display = ('name', 'url', )
    search_fields = ('name', 'url', )


class WebLinkCategoryAdmin(TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label', )


# Register previously defined modeladmins
trek_admin_to_register = [
    (POIType, POITypeAdmin),
    (Theme, ThemeAdmin),
    (TrekNetwork, TrekNetworkAdmin),
    (Usage, UsageAdmin),
    (Route, RouteAdmin),
    (DifficultyLevel, DifficultyLevelAdmin),
    (WebLink, WebLinkAdmin),
    (WebLinkCategory, WebLinkCategoryAdmin),
]

for model, model_admin in trek_admin_to_register:
    admin.site.register(model, model_admin)
