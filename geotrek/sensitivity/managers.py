from geotrek.common.mixins.managers import NoDeleteManager


class SensitiveAreaManager(NoDeleteManager):
    def provider_choices(self):
        providers = self.get_queryset().existing().exclude(provider__exact='') \
            .distinct('provider').values_list('provider', 'provider')
        return providers
