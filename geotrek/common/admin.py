from django.contrib import admin

from .models import FileType, Organism


class OrganismAdmin(admin.ModelAdmin):
    list_display = ('organism', 'structure')
    search_fields = ('organism',)


class FileTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)
    search_fields = ('type',)


admin.site.register(Organism, OrganismAdmin)
admin.site.register(FileType, FileTypeAdmin)
