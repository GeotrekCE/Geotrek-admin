import json
import logging

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models.query import QuerySet


logger = logging.getLogger(__name__)


class TopologyHelper(object):
    @classmethod
    def deserialize(cls, serialized):
        """
        Topologies can be points or lines. Serialized topologies come from Javascript
        module ``topology_helper.js``.

        Example of linear point topology (snapped with path 1245):

            {"lat":5.0, "lng":10.2, "snap":1245}

        Example of linear serialized topology :

        [
            {"offset":0,"positions":{"0":[0,0.3],"1":[0.2,1]},"paths":[1264,1208]},
            {"offset":0,"positions":{"0":[0.2,1],"5":[0,0.2]},"paths":[1208,1263,678,1265,1266,686]}
        ]

        * Each sub-topology represents a way between markers.
        * Start point is first position of sub-topology.
        * End point is last position of sub-topology.
        * All last positions represents intermediary markers.

        Global strategy is :
        * If has lat/lng return point topology
        * Otherwise, create path aggregations from serialized data.
        """
        from .models import Path, PathAggregation
        from .factories import TopologyFactory
        objdict = serialized
        if isinstance(serialized, basestring):
            try:
                objdict = json.loads(serialized)
            except ValueError as e:
                raise ValueError("Invalid serialization: %s" % e)

        if not isinstance(objdict, (list,)):
            lat = objdict.get('lat')
            lng = objdict.get('lng')
            kind = objdict.get('kind')
            # Point topology ?
            if lat and lng:
                return cls._topologypoint(lng, lat, kind, snap=objdict.get('snap'))
            else:
                objdict = [objdict]

        # Path aggregation, remove all existing
        if len(objdict) == 0:
            raise ValueError("Invalid serialized topology : empty list found")
        kind = objdict[0].get('kind')
        offset = objdict[0].get('offset', 0.0)
        topology = TopologyFactory.create(no_path=True, kind=kind, offset=offset)
        PathAggregation.objects.filter(topo_object=topology).delete()
        try:
            counter = 0
            for j, subtopology in enumerate(objdict):
                last_topo = j == len(objdict) - 1
                positions = subtopology.get('positions', {})
                paths = subtopology['paths']
                # Create path aggregations
                for i, path in enumerate(paths):
                    last_path = i == len(paths) - 1
                    # Javascript hash keys are parsed as a string
                    idx = str(i)
                    start_position, end_position = positions.get(idx, (0.0, 1.0))
                    path = Path.objects.get(pk=path)
                    topology.add_path(path, start=start_position, end=end_position, order=counter, reload=False)
                    if not last_topo and last_path:
                        # Intermediary marker.
                        # make sure pos will be [X, X]
                        # [0, X] or [X, 1] or [X, 0] or [1, X] --> X
                        # [0.0, 0.0] --> 0.0  : marker at beginning of path
                        # [1.0, 1.0] --> 1.0  : marker at end of path
                        pos = -1
                        if start_position == end_position:
                            pos = start_position
                        if start_position == 0.0:
                            pos = end_position
                        elif start_position == 1.0:
                            pos = end_position
                        elif end_position == 0.0:
                            pos = start_position
                        elif end_position == 1.0:
                            pos = start_position
                        elif len(paths) == 1:
                            pos = end_position
                        assert pos >= 0, "Invalid position (%s, %s)." % (start_position, end_position)
                        topology.add_path(path, start=pos, end=pos, order=counter, reload=False)
                    counter += 1
        except (AssertionError, ValueError, KeyError, Path.DoesNotExist) as e:
            raise ValueError("Invalid serialized topology : %s" % e)
        topology.save()
        return topology

    @classmethod
    def _topologypoint(cls, lng, lat, kind=None, snap=None):
        """
        Receives a point (lng, lat) with API_SRID, and returns
        a topology objects with a computed path aggregation.
        """
        from .models import Path, PathAggregation
        from .factories import TopologyFactory
        # Find closest path
        point = Point(lng, lat, srid=settings.API_SRID)
        point.transform(settings.SRID)
        if snap is None:
            closest = Path.closest(point)
            position, offset = closest.interpolate(point)
        else:
            closest = Path.objects.get(pk=snap)
            position, offset = closest.interpolate(point)
            offset = 0
        # We can now instantiante a Topology object
        topology = TopologyFactory.create(no_path=True, kind=kind, offset=offset)
        aggrobj = PathAggregation(topo_object=topology,
                                  start_position=position,
                                  end_position=position,
                                  path=closest)
        aggrobj.save()
        point = Point(point.x, point.y, 0, srid=settings.SRID)
        topology.geom = point
        topology.save()
        return topology

    @classmethod
    def serialize(cls, topology):
        # Point topology
        if topology.ispoint():
            geom = topology.geom_as_point()
            point = geom.transform(settings.API_SRID, clone=True)
            objdict = dict(kind=topology.kind, lng=point.x, lat=point.y)
        else:
            # Line topology
            # Fetch properly ordered aggregations
            aggregations = topology.aggregations.select_related('path').all()
            objdict = []
            current = {}
            ipath = 0
            for i, aggr in enumerate(aggregations):
                first = i == 0
                last = i == len(aggregations) - 1
                intermediary = aggr.start_position == aggr.end_position

                current.setdefault('kind', topology.kind)
                current.setdefault('offset', topology.offset)
                if not intermediary:
                    current.setdefault('paths', []).append(aggr.path.pk)
                    if not aggr.is_full or first or last:
                        current.setdefault('positions', {})[ipath] = (aggr.start_position, aggr.end_position)
                ipath = ipath + 1

                if intermediary or last:
                    objdict.append(current)
                    current = {}
                    ipath = 0
        return json.dumps(objdict)

    @classmethod
    def overlapping(cls, klass, queryset):
        from .models import Topology
        if not isinstance(queryset, QuerySet):
            queryset = queryset.__class__.objects.filter(pk=queryset.pk)

        # Shared paths
        paths_pks = queryset.values_list('aggregations__path', flat=True)
        qs = klass.objects.existing().filter(aggregations__path__in=paths_pks)\
                                     .distinct('pk')

        # Filter by kind
        if klass.KIND != Topology.KIND:
            qs = qs.filter(kind=klass.KIND)
        return qs
