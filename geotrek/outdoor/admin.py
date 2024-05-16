from django.conf import settings
from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext as _
from geotrek.common.mixins.actions import MergeActionMixin
from geotrek.outdoor.models import Sector, Practice, SiteType, RatingScale, Rating, CourseType

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin, TabularInline as TranslationTabularInline


@admin.register(Sector)
class SectorAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    merge_field = 'name'


@admin.register(Practice)
class PracticeAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'sector', 'pictogram_img')
    list_filter = ('sector', )
    search_fields = ('name', )
    merge_field = 'name'


@admin.register(SiteType)
class SiteTypeAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'practice')
    list_filter = ('practice', )
    search_fields = ('name', )
    merge_field = 'name'


@admin.register(CourseType)
class CourseTypeAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'practice')
    list_filter = ('practice', )
    search_fields = ('name', )
    merge_field = 'name'


@admin.register(Rating)
class RatingAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'scale', 'order', 'color_markup', 'pictogram_img')
    list_filter = ('scale', 'scale__practice')
    search_fields = ('name', 'description', 'scale__name')
    merge_field = 'name'

    @admin.display(
        description=_("Color")
    )
    def color_markup(self, obj):
        if not obj.color:
            return ''
        return format_html('<span style="color: {code};">⬤</span> {code}', code=obj.color)


class RatingAdminInLine(TranslationTabularInline):
    model = Rating
    extra = 1  # We need one extra to generate Tabbed Translation Tabular inline
    formfield_overrides = {
        models.TextField: {'widget': widgets.AdminTextareaWidget(
            attrs={'rows': 1,
                   'cols': 40,
                   'style': 'height: 1em;'})},
    }


@admin.register(RatingScale)
class RatingScaleAdmin(MergeActionMixin, TabbedTranslationAdmin):
    list_display = ('name', 'practice', 'order')
    list_filter = ('practice', )
    search_fields = ('name', )
    merge_field = 'name'
