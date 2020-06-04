import os

from geotrek.flatpages.models import FlatPage
from geotrek.flatpages.views import FlatPageViewSet, FlatPageMeta

from django.db.models import Q


class SyncRando:
    def __init__(self, sync):
        self.global_sync = sync

    def sync(self, lang):
        self.global_sync.sync_geojson(lang, FlatPageViewSet, 'flatpages.geojson', zipfile=self.global_sync.zipfile)
        flatpages = FlatPage.objects.filter(published=True)
        if self.global_sync.source:
            flatpages = flatpages.filter(source__name__in=self.global_sync.source)
        if self.global_sync.portal:
            flatpages = flatpages.filter(Q(portal__name=self.global_sync.portal) | Q(portal=None))
        for flatpage in flatpages:
            name = os.path.join('meta', lang, flatpage.rando_url, 'index.html')
            self.global_sync.sync_view(lang, FlatPageMeta.as_view(), name, pk=flatpage.pk,
                                       params={'rando_url': self.global_sync.rando_url})
