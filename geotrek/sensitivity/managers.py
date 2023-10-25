from geotrek.common.mixins.managers import NoDeleteManager, ProviderChoicesMixin


class SensitiveAreaManager(NoDeleteManager, ProviderChoicesMixin):
    pass
