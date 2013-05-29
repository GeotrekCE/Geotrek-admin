from django.contrib import admin

from .models import FileType, Organism


class OrganismAdmin(admin.ModelAdmin):
    list_display = ('organism', 'structure')
    search_fields = ('organism', 'structure')
    list_filter = ('structure',)


class FileTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)


admin.site.register(Organism, OrganismAdmin)
admin.site.register(FileType, FileTypeAdmin)
