from django.contrib import admin
from geotrek.sensitivity.models import SportPractice, Species


class SportPracticeAdmin(admin.ModelAdmin):
    pass


class SpeciesAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super(SpeciesAdmin, self).get_queryset(request).filter(category=Species.SPECIES)


admin.site.register(SportPractice, SportPracticeAdmin)
admin.site.register(Species, SpeciesAdmin)
