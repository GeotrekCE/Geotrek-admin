from django.contrib import admin

from geotrek.common.mixins.actions import MergeActionMixin
from geotrek.sensitivity.models import Rule, SportPractice, Species


@admin.register(Rule)
class RuleAdmin(MergeActionMixin, admin.ModelAdmin):
    merge_field = "name"
    list_display = ('name', 'code', )
    search_fields = ('name', 'code', )


@admin.register(SportPractice)
class SportPracticeAdmin(MergeActionMixin, admin.ModelAdmin):
    merge_field = "name"


@admin.register(Species)
class SpeciesAdmin(MergeActionMixin, admin.ModelAdmin):
    merge_field = "name"

    def get_queryset(self, request):
        return super().get_queryset(request).filter(category=Species.SPECIES)
