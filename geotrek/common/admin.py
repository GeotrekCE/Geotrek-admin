from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from modeltranslation.admin import TranslationAdmin
from paperclip.models import Attachment
from .models import FileType, Organism, Theme, CirkwiTag


class OrganismAdmin(admin.ModelAdmin):
    list_display = ('organism', 'structure')
    search_fields = ('organism', 'structure')
    list_filter = ('structure',)


class FileTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)


class MapEntityContentTypeFilter(admin.SimpleListFilter):
    title = _('content type')
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        from mapentity import registry
        values = []
        for model, entity in registry.registry.items():
            content_type = model.get_content_type_id()
            values.append((content_type, entity.label))
        return tuple(values)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type=self.value())


class AttachmentAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_update'
    search_fields = ('title', 'legend', 'author')
    list_display = ('title', 'legend', 'author', 'content_type')
    list_filter = ('filetype', MapEntityContentTypeFilter)
    readonly_fields = ('content_type', 'object_id', 'creator', 'title')

    def has_add_permission(self, request):
        """ Do not add from Adminsite.
        """
        return False


class CirkwiAdmin(admin.ModelAdmin):
    list_display = ('name', 'eid')
    search_fields = ('name', '=eid')


class ThemeAdmin(TranslationAdmin):
    list_display = ('label', 'cirkwi', 'pictogram_img')
    search_fields = ('label',)


admin.site.register(Organism, OrganismAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(FileType, FileTypeAdmin)
admin.site.register(CirkwiTag, CirkwiAdmin)
admin.site.register(Theme, ThemeAdmin)
