from mapentity.filters import MapEntityFilterSet

from .models import Dive


class DiveFilterSet(MapEntityFilterSet):
    class Meta:
        model = Dive
        fields = ['published', 'difficulty', 'levels', 'themes',
                  'practice', 'structure', 'source', 'portal']
