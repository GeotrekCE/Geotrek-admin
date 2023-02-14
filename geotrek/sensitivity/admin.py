from django.contrib import admin

from geotrek.common.mixins.actions import MergeActionMixin
from geotrek.sensitivity.models import Rule, SportPractice, Species


class RuleAdmin(MergeActionMixin, admin.ModelAdmin):
    merge_field = "name"
    list_display = ('name', 'code', )
    search_fields = ('name', 'code', )


class SportPracticeAdmin(MergeActionMixin, admin.ModelAdmin):
    merge_field = "name"


class SpeciesAdmin(MergeActionMixin, admin.ModelAdmin):
    merge_field = "name"

    def get_queryset(self, request):
        return super().get_queryset(request).filter(category=Species.SPECIES)


admin.site.register(Rule, RuleAdmin)
admin.site.register(SportPractice, SportPracticeAdmin)
admin.site.register(Species, SpeciesAdmin)
