from django.contrib import admin

from geotrek.common.mixins import MergeActionMixin
from geotrek.sensitivity.models import SportPractice, Species


class SportPracticeAdmin(MergeActionMixin, admin.ModelAdmin):
    merge_field = "name"


class SpeciesAdmin(MergeActionMixin, admin.ModelAdmin):
    merge_field = "name"

    def get_queryset(self, request):
        return super(SpeciesAdmin, self).get_queryset(request).filter(category=Species.SPECIES)


admin.site.register(SportPractice, SportPracticeAdmin)
admin.site.register(Species, SpeciesAdmin)
