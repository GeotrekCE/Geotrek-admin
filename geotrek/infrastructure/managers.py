from geotrek.common.mixins.managers import NoDeleteManager


class InfrastructureGISManager(NoDeleteManager):
    """ Override default typology mixin manager"""
    def implantation_year_choices(self):
        all_years = self.get_queryset().existing().filter(implantation_year__isnull=False) \
            .order_by('-implantation_year').distinct('implantation_year') \
            .values_list('implantation_year', 'implantation_year')
        return all_years

    def provider_choices(self):
        providers = self.get_queryset().existing().exclude(provider__exact='') \
            .distinct('provider').values_list('provider', 'provider')
        return providers
