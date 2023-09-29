from geotrek.common.mixins.managers import NoDeleteManager


class InfrastructureGISManager(NoDeleteManager):
    """ Override default typology mixin manager"""
    def implantation_year_choices(self):
        values = self.get_queryset().existing().filter(implantation_year__isnull=False)\
            .order_by('-implantation_year').distinct('implantation_year') \
            .values_list('implantation_year', flat=True)
        return tuple((value, value) for value in values)

    def provider_choices(self):
        providers = self.get_queryset().existing().exclude(provider__exact='') \
            .distinct('provider').values_list('provider', 'provider')
        return providers
