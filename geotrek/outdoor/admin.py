from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _
from geotrek.common.admin import MergeActionMixin
from geotrek.outdoor.models import Sector, Practice, SiteType, RatingScale, Rating

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin
else:
    TranslationAdmin = admin.ModelAdmin


@admin.register(Sector)
class SectorAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    merge_field = 'name'


@admin.register(Practice)
class PracticeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'sector', 'pictogram_img')
    list_filter = ('sector', )
    search_fields = ('name', )
    merge_field = 'name'


@admin.register(SiteType)
class SiteTypeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'practice')
    list_filter = ('practice', )
    search_fields = ('name', )
    merge_field = 'name'


@admin.register(RatingScale)
class RatingScaleAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'practice', 'order')
    list_filter = ('practice', )
    search_fields = ('name', )
    merge_field = 'name'


@admin.register(Rating)
class RatingAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'scale', 'order', 'color_markup', 'pictogram_img')
    list_filter = ('scale', 'scale__practice')
    search_fields = ('name', 'description', 'scale__name')
    merge_field = 'name'

    def color_markup(self, obj):
        if not obj.color:
            return ''
        return format_html('<span style="color: {code};">⬤</span> {code}', code=obj.color)
    color_markup.short_description = _("Color")
