import os.path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry

from geotrek.core.helpers import TopologyHelper

from geotrek.infrastructure.models import Infrastructure, InfrastructureType, InfrastructureCondition

from geotrek.authent.models import Structure



class Command(BaseCommand):
    args = '<point_layer>'
    help = 'Load a layer with point geometries in a model\n'
    can_import_settings = True
    field_name = 'name'
    field_infrastructure_type = 'type'
    field_condition_type = 'etat'
    field_structure_type = 'structure'
    field_description='desc'

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

            infra = feature.GetFieldAsString(self.field_infrastructure_type)
            if infra:
                infra = infra.decode('utf-8')

            condition = feature.GetFieldAsString(self.field_condition_type)
            if condition:
                condition = condition.decode('utf-8')

            structure = feature.GetFieldAsString(self.field_structure_type)
            if structure:
                structure = structure.decode('utf-8')

            description = feature.GetFieldAsString(self.field_description)
            if description:
                description = description.decode('utf-8')

            self.create_infrastructure(geometry, name, infra, condition, structure, description)




    def create_infrastructure(self, geometry, name, infra, condition, structure, description ):
        infraType, created = InfrastructureType.objects.get_or_create(label=infra)
        condition_type, created = InfrastructureCondition.objects.get_or_create(label=condition)
        structure_type, created = Structure.objects.get_or_create(name=structure)


        infra = Infrastructure.objects.create(type=infraType, name=name, condition=condition_type, structure=structure_type, description=description)
        # Use existing topology helpers to transform a Point(x, y)
        # to a path aggregation (topology)
        serialized = '{"lng": %s, "lat": %s}' % (geometry.x, geometry.y)
        topology = TopologyHelper.deserialize(serialized)
        # Move deserialization aggregations to the POI
        infra.mutate(topology)
        return infra