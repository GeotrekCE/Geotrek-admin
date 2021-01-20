from django.utils.translation import gettext_lazy as _
from .models import RestrictedArea, District, City
from geotrek.common.utils import intersecting


class ZoningPropertiesMixin:
    areas_verbose_name = _("Restricted areas")

    @property
    def zoning_property(self):
        return self

    @property
    def areas(self):
        return intersecting(RestrictedArea, self.zoning_property, distance=0)

    @property
    def districts(self):
        return intersecting(District, self.zoning_property, distance=0)

    @property
    def cities(self):
        return intersecting(City, self.zoning_property, distance=0)

    @property
    def published_areas(self):
        if not hasattr(self, 'published'):
            return self.areas
        return self.areas.filter(published=True)

    @property
    def published_districts(self):
        if not hasattr(self, 'published'):
            return self.districts
        return self.districts.filter(published=True)

    @property
    def published_cities(self):
        if not hasattr(self, 'published'):
            return self.cities
        return self.cities.filter(published=True)
