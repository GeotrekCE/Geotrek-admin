import json
import logging

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

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
        ____________________________________________________________________________________________
        Without Dynamic Segmentation :

        Deserialize normally and create a topology from the geojson
        """
        from .models import Path, Topology, PathAggregation
        try:
            return Topology.objects.get(pk=int(serialized))
        except Topology.DoesNotExist:
            raise
        except (TypeError, ValueError):
            pass  # value is not integer, thus should be deserialized
        if not settings.TREKKING_TOPOLOGY_ENABLED:
            return Topology.objects.create(kind='TMP', geom=GEOSGeometry(serialized, srid=settings.API_SRID))
        objdict = serialized
        if isinstance(serialized, str):
            try:
                objdict = json.loads(serialized)
            except ValueError as e:
                raise ValueError("Invalid serialization: %s" % e)

        if objdict and not isinstance(objdict, list):
            lat = objdict.get('lat')
            lng = objdict.get('lng')
            pk = objdict.get('pk')
            kind = objdict.get('kind')
            # Point topology ?
            if lat is not None and lng is not None:
                if pk:
                    try:
                        return Topology.objects.get(pk=int(pk))
                    except (Topology.DoesNotExist, ValueError):
                        pass

                return Topology._topologypoint(lng, lat, kind, snap=objdict.get('snap'))
            else:
                objdict = [objdict]

        if not objdict:
            raise ValueError("Invalid serialized topology : empty list found")

        # If pk is still here, the user did not edit it.
        # Return existing topology instead
        pk = objdict[0].get('pk')
        if pk:
            try:
                return Topology.objects.get(pk=int(pk))
            except (Topology.DoesNotExist, ValueError):
                pass

        offset = objdict[0].get('offset', 0.0)
        topology = Topology.objects.create(kind='TMP', offset=offset)
        try:
            counter = 0
            for j, subtopology in enumerate(objdict):
                last_topo = j == len(objdict) - 1
                positions = subtopology.get('positions', {})
                paths = subtopology['paths']
                # Create path aggregations
                aggrs = []
                for i, path in enumerate(paths):
                    last_path = i == len(paths) - 1
                    # Javascript hash keys are parsed as a string
                    idx = str(i)
                    start_position, end_position = positions.get(idx, (0.0, 1.0))
                    path = Path.objects.get(pk=path)
                    aggrs.append(PathAggregation(
                        path=path,
                        topo_object=topology,
                        start_position=start_position,
                        end_position=end_position,
                        order=counter
                    ))
                    if not last_topo and last_path:
                        counter += 1
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
                        aggrs.append(PathAggregation(
                            path=path,
                            topo_object=topology,
                            start_position=pos,
                            end_position=pos,
                            order=counter
                        ))
                    counter += 1
                PathAggregation.objects.bulk_create(aggrs)
        except (AssertionError, ValueError, KeyError, Path.DoesNotExist) as e:
            raise ValueError("Invalid serialized topology : %s" % e)
        topology.save()
        return topology
