# -*- coding: utf-8 -*-

import os.path

from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geotrek.authent.models import Structure
from geotrek.core.helpers import TopologyHelper
from geotrek.infrastructure.models import Signage, InfrastructureType, InfrastructureCondition, Infrastructure
from django.conf import settings


class Command(BaseCommand):
    help = 'Load a layer with point geometries in te structure model\n'
    can_import_settings = True
    counter = 0

    def add_arguments(self, parser):
        parser.add_argument('point_layer')
        parser.add_argument('--signage', dest='signage', action='store_true', help='Create signage objects')
        parser.add_argument('--infrastructure', dest='infrastructure', action='store_true',
                            help='Create infrastructure objects')
        parser.add_argument('--encoding', '-e', action='store', dest='encoding', default='utf-8',
                            help='File encoding, default utf-8')
        parser.add_argument('--name-field', '-n', action='store', dest='name_field', help='Base url')
        parser.add_argument('--type-field', '-t', action='store', dest='type_field', help='Base url')
        parser.add_argument('--condition-field', '-c', action='store', dest='condition_field', help='Base url')
        parser.add_argument('--structure-field', '-s', action='store', dest='structure_field', help='Base url')
        parser.add_argument('--description-field', '-d', action='store', dest='description_field', help='Base url')
        parser.add_argument('--year-field', '-y', action='store', dest='year_field', help='Base url')
        parser.add_argument('--type-default', action='store', dest='type_default', help='Base url')
        parser.add_argument('--name-default', action='store', dest='name_default', help='Base url')
        parser.add_argument('--condition-default', action='store', dest='condition_default', help='Base url')
        parser.add_argument('--structure-default', action='store', dest='structure_default', help='Base url')
        parser.add_argument('--description-default', action='store', dest='description_default', default="",
                            help='Base url')
        parser.add_argument('--year-default', action='store', dest='year_default', help='Base url')

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')
        try:
            from osgeo import gdal, ogr, osr  # NOQA

        except ImportError:
            raise CommandError('GDAL Python bindings are not available. Can not proceed.')

        filename = options['point_layer']

        if not os.path.exists(filename):
            raise CommandError('File does not exists at: %s' % filename)

        if (options.get('signage') and (options.get('infrastructure')))\
                or (not options.get('signage') and (not options.get('infrastructure'))):
                raise CommandError('Only one of --signage and --infrastructure required')

        data_source = DataSource(filename, encoding=options.get('encoding'))

        field_name = options.get('name_field')
        field_infrastructure_type = options.get('type_field')
        field_condition_type = options.get('condition_field')
        field_structure_type = options.get('structure_field')
        field_description = options.get('description_field')
        field_implantation_year = options.get('year_field')

        sid = transaction.savepoint()

        try:
            for layer in data_source:
                if verbosity >= 2:
                    self.stdout.write("- Layer '{}' with {} objects found".format(layer.name, layer.num_feat))
                available_fields = layer.fields
                if (field_infrastructure_type and field_infrastructure_type not in available_fields)\
                        or (not field_infrastructure_type and not options.get('type_default')):
                    self.stdout.write(self.style.ERROR(
                        "Field '{}' not found in data source.".format(field_infrastructure_type)))
                    self.stdout.write(self.style.ERROR(
                        "Set it with --type-field, or set a default value with --type-default"))
                    break
                if (field_name and field_name not in available_fields)\
                        or (not field_name and not options.get('name_default')):
                    self.stdout.write(self.style.ERROR(
                        "Field '{}' not found in data source.".format(field_name)))
                    self.stdout.write(self.style.ERROR(
                        "Set it with --name-field, or set a default value with --name-default"))
                    break
                if (field_condition_type and field_condition_type not in available_fields)\
                        or (not field_condition_type and not options.get('condition_default')):
                    self.stdout.write(self.style.ERROR(
                        "Field '{}' not found in data source.".format(field_condition_type)))
                    self.stdout.write(self.style.ERROR(
                        "Set it with --condition-field, or set a default value with --condition-default"))
                    break
                if (field_structure_type and field_structure_type not in available_fields)\
                        or (not field_structure_type and not options.get('structure_default')):
                    self.stdout.write(self.style.ERROR(
                        "Field '{}' not found in data source.".format(field_structure_type)))
                    self.stdout.write(self.style.ERROR(
                        "Set it with --structure-field, or set a default value with --structure-default"))
                    break
                if (field_description and field_description not in available_fields)\
                        or (not field_condition_type and not options.get('description_default')):
                    self.stdout.write(self.style.ERROR(
                        "Field '{}' not found in data source.".format(field_description)))
                    self.stdout.write(self.style.ERROR(
                        "Set it with --description-field, or set a default value with --description-default"))
                    break
                if (field_implantation_year and field_implantation_year not in available_fields) \
                        or (not field_condition_type and not options.get('year_default')):
                    self.stdout.write(
                        self.style.ERROR("Field '{}' not found in data source.".format(field_implantation_year)))
                    self.stdout.write(self.style.ERROR(
                        "Set it with --implantation-field, or set a default value with --implantation-default"))
                    break

                for feature in layer:
                    feature_geom = feature.geom.transform(settings.API_SRID, clone=True)
                    feature_geom.coord_dim = 2

                    name = feature.get(field_name) if field_name in available_fields else options.get('name_default')
                    type = feature.get(
                        field_infrastructure_type) if field_infrastructure_type in available_fields else options.get(
                        'type_default')
                    condition = feature.get(
                        field_condition_type) if field_condition_type in available_fields else options.get(
                        'condition_default')
                    structure = feature.get(
                        field_structure_type) if field_structure_type in available_fields else options.get(
                        'structure_default')
                    description = feature.get(field_description) if field_description in available_fields else options.get(
                        'description_default')
                    year = int(feature.get(
                        field_implantation_year)) if field_implantation_year in available_fields else options.get(
                        'year_default')

                    model = 'S' if options.get('signage') else 'B'

                    self.create_infrastructure(feature_geom, name, type, condition, structure, description, year, model, verbosity)

            transaction.savepoint_commit(sid)
            if verbosity >= 2:
                self.stdout.write(self.style.NOTICE("{} objects created.".format(self.counter)))

        except Exception:
            self.stdout.write(self.style.ERROR("An error occured, rolling back operations."))
            transaction.savepoint_rollback(sid)
            raise

    def create_infrastructure(self, geometry, name, type, condition, structure, description, year, model, verbosity):

        infra_type, created = InfrastructureType.objects.get_or_create(label=type, type=model)

        if created and verbosity:
            self.stdout.write("- InfrastructureType '{}' created".format(infra_type))

        condition_type, created = InfrastructureCondition.objects.get_or_create(label=condition)

        if created and verbosity:
            self.stdout.write("- Condition Type '{}' created".format(condition_type))

        structure, created = Structure.objects.get_or_create(name=structure)

        if created and verbosity:
            self.stdout.write("- Structure '{}' created".format(structure))
        with transaction.atomic():
            Model = Signage if model == 'S' else Infrastructure
            infra = Model.objects.create(
                type=infra_type,
                name=name,
                condition=condition_type,
                structure=structure,
                description=description,
                implantation_year=year
            )
        serialized = '{"lng": %s, "lat": %s}' % (geometry.x, geometry.y)
        topology = TopologyHelper.deserialize(serialized)
        infra.mutate(topology)

        self.counter += 1

        return infra
