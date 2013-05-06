from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from geotrek.common.models import Organism, FileType


class OrganismAdmin(admin.ModelAdmin):
    list_display = ('organism',)
    search_fields = ('organism',)


class FileTypeAdmin(TranslationAdmin):
    list_display = ('type',)
    search_fields = ('type',)


admin.site.register(Organism, OrganismAdmin)
admin.site.register(FileType, FileTypeAdmin)
