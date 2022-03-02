import os

from geotrek.sensitivity import views, models


class SyncRando:
    def __init__(self, sync):
        self.global_sync = sync

    def sync(self, lang):
        self.global_sync.sync_geojson(lang, views.SensitiveAreaViewSet, 'sensitiveareas.geojson',
                                      type_views={"get": "rando-v2-geojson"}, params={'practices': 'Terrestre'})
        for area in models.SensitiveArea.objects.existing().filter(published=True):
            name = os.path.join('api', lang, 'sensitiveareas', '{obj.pk}.kml'.format(obj=area))
            self.global_sync.sync_view(lang, views.SensitiveAreaKMLDetail.as_view(), name, pk=area.pk)
            self.global_sync.sync_media_file(lang, area.species.pictogram)
