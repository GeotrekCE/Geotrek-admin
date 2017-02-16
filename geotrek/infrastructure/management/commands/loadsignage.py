# -*- coding: utf8 -*-

import os.path
from optparse import make_option

from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geotrek.authent.models import Structure
from geotrek.core.helpers import TopologyHelper
from geotrek.infrastructure.models import Signage, InfrastructureType, InfrastructureCondition
from django.conf import settings


class Command(BaseCommand):
    args = '<point_layer>'
    help = 'Load a layer with point geometries in a model\n'
    can_import_settings = True
    counter = 0

    option_list = BaseCommand.option_list + (
        make_option('--encoding', '-e', action='store', dest='encoding',
                    default='utf-8', help='File encoding, default utf-8'),
        make_option('--name-field', '-n', action='store', dest='name-field',
                    help='Base url'),
        make_option('--type-field', '-t', action='store', dest='type-field',
                    help='Base url'),
        make_option('--condition-field', '-c', action='store', dest='condition-field',
                    help='Base url'),
        make_option('--structure-field', '-s', action='store', dest='structure-field',
                    help='Base url'),
        make_option('--description-field', '-d', action='store', dest='description-field',
                    help='Base url'),
        make_option('--year-field', '-y', action='store', dest='year-field',
                    help='Base url'),
        make_option('--name-default', action='store', dest='name-default',
                    help='Base url'),
        make_option('--type-default', action='store', dest='type-default',
                    help='Base url'),
        make_option('--condition-default', action='store', dest='condition-default',
                    help='Base url'),
        make_option('--structure-default', action='store', dest='structure-default',
                    help='Base url'),
        make_option('--description-default', action='store', dest='description-default',
                    default="", help='Base url'),
        make_option('--year-default', action='store', dest='year-default',
                    help='Base url'),
    )

    def handle(self, *args, **options):
        try:
            from osgeo import gdal, ogr, osr  # NOQA

        except ImportError:
            raise CommandError('GDAL Python bindings are not available. Can not proceed.')

        # Validate arguments
        if len(args) != 1:
            raise CommandError('Filename missing. See help')

        filename = args[0]

        if not os.path.exists(filename):
            raise CommandError('File does not exists at: %s' % filename)

        data_source = DataSource(filename, encoding=options.get('encoding'))

        field_name = options.get('name-field')
        field_infrastructure_type = options.get('type-field')
        field_condition_type = options.get('condition-field')
        field_structure_type = options.get('structure-field')
        field_description = options.get('description-field')
        field_implantation_year = options.get('year-field')

        sid = transaction.savepoint()

        try:
            for layer in data_source:
                self.stdout.write("- Layer '{}' with {} objects found".format(layer.name, layer.num_feat))
                available_fields = layer.fields

                if (field_name and field_name not in available_fields)\
                        or (not field_name and not options.get('name-default')):
                    self.stdout.write(self.style.ERROR("Field '{}' not found in data source.".format(field_name)))
                    self.stdout.write(self.style.ERROR(
                        u"Set it with --name-field, or set a default value with --name-default"))
                    break
                if (field_infrastructure_type and field_infrastructure_type not in available_fields)\
                        or (not field_infrastructure_type and not options.get('type-default')):
                    self.stdout.write(
                        self.style.ERROR("Field '{}' not found in data source.".format(field_infrastructure_type)))
                    self.stdout.write(self.style.ERROR(
                        u"Set it with --type-field, or set a default value with --type-default"))
                    break
                if (field_condition_type and field_condition_type not in available_fields)\
                        or (not field_condition_type and not options.get('condition-default')):
                    self.stdout.write(self.style.ERROR("Field '{}' not found in data source.".format(field_condition_type)))
                    self.stdout.write(self.style.ERROR(
                        u"Set it with --condition-field, or set a default value with --condition-default"))
                    break
                if (field_structure_type and field_structure_type not in available_fields)\
                        or (not field_structure_type and not options.get('structure-default')):
                    self.stdout.write(self.style.ERROR("Field '{}' not found in data source.".format(field_structure_type)))
                    self.stdout.write(self.style.ERROR(
                        u"Set it with --structure-field, or set a default value with --structure-default"))
                    break
                if field_description and field_description not in available_fields:
                    self.stdout.write(self.style.ERROR("Field '{}' not found in data source.".format(field_description)))
                    self.stdout.write(self.style.ERROR(
                        u"Set it with --description-field, or set a default value with --description-default"))
                    break
                if field_implantation_year and field_implantation_year not in available_fields:
                    self.stdout.write(
                        self.style.ERROR(u"Field '{}' not found in data source.".format(field_implantation_year)))
                    self.stdout.write(self.style.ERROR(
                        u"Set it with --implantation-field, or set a default value with --implantation-default"))
                    break

                for feature in layer:
                    feature_geom = feature.geom.transform(settings.API_SRID, clone=True)
                    feature_geom.coord_dim = 2

                    name = feature.get(field_name) if field_name in available_fields else options.get('name-default')
                    infra = feature.get(
                        field_infrastructure_type) if field_infrastructure_type in available_fields else options.get(
                        'type-default')
                    condition = feature.get(
                        field_condition_type) if field_condition_type in available_fields else options.get(
                        'condition-default')
                    structure = feature.get(
                        field_structure_type) if field_structure_type in available_fields else options.get(
                        'structure-default')
                    description = feature.get(field_description) if field_description in available_fields else options.get(
                        'description-default')
                    year = int(feature.get(
                        field_implantation_year)) if field_implantation_year in available_fields else options.get(
                        'year-default')

                    self.create_signage(feature_geom, name, infra, condition, structure, description, year)

            transaction.savepoint_commit(sid)
            self.stdout.write(self.style.NOTICE(u"{} objects created.".format(self.counter)))

        except Exception:
            self.stdout.write(self.style.ERROR(u"An error occured, rolling back operations."))
            transaction.savepoint_rollback(sid)
            raise

    def create_signage(self, geometry, name, infra, condition, structure, description, year):
        infra_type, created = InfrastructureType.objects.get_or_create(label=infra, type='S')

        if created:
            self.stdout.write(u"- InfrastructureType '{}' created".format(infra_type))

        condition_type, created = InfrastructureCondition.objects.get_or_create(label=condition)

        if created:
            self.stdout.write(u"- Condition Type '{}' created".format(condition_type))

        structure, created = Structure.objects.get_or_create(name=structure)

        if created:
            self.stdout.write(u"- Structure '{}' created".format(structure))

        infra = Signage.objects.create(
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
