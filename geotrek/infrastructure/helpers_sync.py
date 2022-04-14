from geotrek.infrastructure import models
from geotrek.infrastructure.views import InfrastructureAPIViewSet


class SyncRando:
    def __init__(self, sync):
        self.global_sync = sync

    def sync(self, lang):
        self.global_sync.sync_geojson(lang, InfrastructureAPIViewSet, 'infrastructures.geojson')
        self.global_sync.sync_static_file(lang, 'infrastructure/picto-infrastructure.png')
        models_picto = [models.InfrastructureType]
        self.global_sync.sync_pictograms(lang, models_picto, zipfile=self.global_sync.zipfile)
