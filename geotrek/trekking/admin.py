# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from tinymce.widgets import TinyMCE

from geotrek.authent.admin import TrekkingManagerModelAdmin
from .models import (
    POIType, Theme, TrekNetwork, Usage, Route, DifficultyLevel, WebLink,
    WebLinkCategory, InformationDesk
)


class POITypeAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label',)


class ThemeAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label',)


class TrekNetworkAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('network',)
    search_fields = ('network',)


class UsageAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('usage', 'pictogram_img')
    search_fields = ('usage',)


class RouteAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('route',)
    search_fields = ('route',)


class DifficultyLevelAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('difficulty',)
    search_fields = ('difficulty',)


class WebLinkAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('name', 'url', )
    search_fields = ('name', 'url', )


class WebLinkCategoryAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('label', 'pictogram_img')
    search_fields = ('label', )


class InformationDeskAdmin(TrekkingManagerModelAdmin, TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE},
    }


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
    (InformationDesk, InformationDeskAdmin),
]

for model, model_admin in trek_admin_to_register:
    admin.site.register(model, model_admin)
