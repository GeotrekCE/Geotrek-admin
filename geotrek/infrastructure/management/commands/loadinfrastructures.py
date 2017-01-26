import os.path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry

from geotrek.core.helpers import TopologyHelper

from geotrek.infrastructure.models import Infrastructure, InfrastructureType, InfrastructureCondition


class Command(BaseCommand):
    args = '<point_layer>'
    help = 'Load a layer with point geometries in a model\n'
    can_import_settings = True
    field_name = 'name'
    field_infrastructure_type = 'type'
    field_condition_type = 'etat'

    def handle(self, *args, **options):

        try:
            from osgeo import gdal, ogr, osr  # NOQA
        except ImportError:
            msg = 'GDAL Python bindings are not available. Can not proceed.'
            raise CommandError(msg)

        # Validate arguments
        if len(args) != 1:
            raise CommandError('Filename missing. See help')

        filename = args[0]

        if not os.path.exists(filename):
            raise CommandError('File does not exists at: %s' % filename)

        ogrdriver = ogr.GetDriverByName("ESRI Shapefile")
        datasource = ogrdriver.Open(filename, 1)
        layer = datasource.GetLayer()
        count = layer.GetFeatureCount()
        self.stdout.write('%s objects found' % count)

        for i in range(count):
            feature = layer.GetFeature(i)
            featureGeom = feature.GetGeometryRef()
            geometry = GEOSGeometry(featureGeom.ExportToWkt())
            name = feature.GetFieldAsString(self.field_name)

            if name:
                name = name.decode('utf-8')

            infra_type = feature.GetFieldAsString(self.field_infrastructure_type)
            if infra_type:
                infra_type = infra_type.decode('utf-8')

            #ajout theo
            etat = feature.GetFieldAsString(self.field_condition_type)
            if etat:
                etat = etat.decode('utf-8')

            self.create_infrastructure(geometry, name, infra_type, etat)




    def create_infrastructure(self, geometry, name, infra_type, etat ):
        infraType, created = InfrastructureType.objects.get_or_create(label=infra_type)
        etatType, created = InfrastructureCondition.objects.get_or_create(label=etat)

        infra = Infrastructure.objects.create(type=infraType, name=name, condition=etatType)
        # Use existing topology helpers to transform a Point(x, y)
        # to a path aggregation (topology)
        serialized = '{"lng": %s, "lat": %s}' % (geometry.x, geometry.y)
        topology = TopologyHelper.deserialize(serialized)
        # Move deserialization aggregations to the POI
        infra.mutate(topology)
        return infra
