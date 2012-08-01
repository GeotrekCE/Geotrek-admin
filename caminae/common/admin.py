from django.contrib import admin

from caminae.common.models import Organism, FileType


class OrganismAdmin(admin.ModelAdmin):
    list_display = ('organism',)
    search_fields = ('organism',)


class FileTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)
    search_fields = ('type',)


admin.site.register(Organism, OrganismAdmin)
admin.site.register(FileType, FileTypeAdmin)
