from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ForeignKey, ManyToManyField
from . import models as common_models

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin
else:
    TranslationAdmin = admin.ModelAdmin


def apply_merge(modeladmin, request, queryset):
    main = queryset[0]
    tail = queryset[1:]
    if not tail:
        return
    name = ' + '.join(queryset.values_list(modeladmin.merge_field, flat=True))
    related = main._meta.get_fields()

    for r in related:
        if r.remote_field:
            remote_field = r.remote_field.name
            if isinstance(r.remote_field, ForeignKey):
                r.remote_field.model.objects.filter(**{'%s__in' % remote_field: tail}).update(**{remote_field: main})
            elif isinstance(r.remote_field, ManyToManyField):
                for element in r.remote_field.model.objects.filter(**{'%s__in' % remote_field: tail}):
                    getattr(element, remote_field).add(main)

    setattr(main, modeladmin.merge_field, name)
    main.save()
    for element_to_delete in tail:
        element_to_delete.delete()


apply_merge.short_description = _('Apply merge')


class MergeActionMixin(object):
    actions = [apply_merge, ]


class OrganismAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('organism', 'structure')
    search_fields = ('organism', 'structure')
    list_filter = ('structure',)
    merge_field = 'organism'


class FileTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)
    merge_field = 'type'


class MapEntityContentTypeFilter(admin.SimpleListFilter):
    title = _('content type')
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        from mapentity.registry import registry
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


class ThemeAdmin(MergeActionMixin, TranslationAdmin):
    list_display = ('label', 'cirkwi', 'pictogram_img')
    search_fields = ('label',)
    merge_field = 'label'


class RecordSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'pictogram_img')
    search_fields = ('name', )


class TargetPortalAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name', 'website')


admin.site.register(common_models.Organism, OrganismAdmin)
admin.site.register(common_models.Attachment, AttachmentAdmin)
admin.site.register(common_models.FileType, FileTypeAdmin)
admin.site.register(common_models.Theme, ThemeAdmin)
admin.site.register(common_models.RecordSource, RecordSourceAdmin)
admin.site.register(common_models.TargetPortal, TargetPortalAdmin)
