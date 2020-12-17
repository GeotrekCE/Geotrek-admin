from django.conf import settings
from django.contrib import admin
from geotrek.common.admin import MergeActionMixin
from geotrek.outdoor.models import Practice, SiteType

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin
else:
    TranslationAdmin = admin.ModelAdmin


@admin.register(Practice)
class PracticeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    merge_field = 'name'


@admin.register(SiteType)
class SiteTypeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('name', 'practice')
    list_filter = ('practice', )
    search_fields = ('name', )
    merge_field = 'name'
