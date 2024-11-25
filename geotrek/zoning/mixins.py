import hashlib

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from geotrek.common.utils import intersecting, uniquify
from .models import RestrictedArea, District, City


class ZoningPropertiesMixin:
    areas_verbose_name = _("Restricted areas")

    @property
    def zoning_property(self):
        return self

    def get_areas(self):
        return uniquify(intersecting(RestrictedArea,
                                     self.zoning_property,
                                     distance=0,
                                     defer=('geom',)).select_related('area_type'))

    @property
    def areas(self):
        last_update_and_count = RestrictedArea.last_update_and_count
        last_update_iso_format = last_update_and_count['last_update'].isoformat() if last_update_and_count[
            'last_update'] else 'no-data'
        count = last_update_and_count['count']
        cache_string = f"areas:{self.pk}:{self.date_update.isoformat()}:{last_update_iso_format}:{count}"
        cache_key = hashlib.md5(cache_string.encode("utf-8")).hexdigest()
        if cache_key in cache:
            return cache.get(cache_key)
        areas = self.get_areas()
        cache.set(cache_key, areas)
        return areas

    def get_districts(self):
        return uniquify(intersecting(District, self.zoning_property, distance=0, defer=('geom',)))

    @property
    def districts(self):
        last_update_and_count = District.last_update_and_count
        last_update_iso_format = last_update_and_count['last_update'].isoformat() if last_update_and_count['last_update'] else 'no-data'
        count = last_update_and_count['count']
        cache_string = f"districts:{self.pk}:{self.date_update.isoformat()}:{last_update_iso_format}:{count}"
        cache_key = hashlib.md5(cache_string.encode("utf-8")).hexdigest()
        if cache_key in cache:
            return cache.get(cache_key)
        districts = self.get_districts()
        cache.set(cache_key, districts)
        return districts

    def get_cities(self):
        return uniquify(intersecting(City, self.zoning_property, distance=0, defer=('geom',)))

    @property
    def cities(self):
        last_update_and_count = City.last_update_and_count
        last_update_iso_format = last_update_and_count['last_update'].isoformat() if last_update_and_count[
            'last_update'] else 'no-data'
        count = last_update_and_count['count']
        cache_string = f"cities:{self.pk}:{self.date_update.isoformat()}:{last_update_iso_format}:{count}"
        cache_key = hashlib.md5(cache_string.encode("utf-8")).hexdigest()
        data = cache.get(cache_key)
        if data:
            return data

        cities = self.get_cities()
        cache.set(cache_key, cities)
        return cities

    @property
    def published_areas(self):
        if not hasattr(self, 'published'):
            return self.areas
        return [area for area in self.areas if area.published]

    @property
    def published_districts(self):
        if not hasattr(self, 'published'):
            return self.districts
        return [district for district in self.districts if district.published]

    @property
    def published_cities(self):
        if not hasattr(self, 'published'):
            return self.cities
        return [city for city in self.cities if city.published]
