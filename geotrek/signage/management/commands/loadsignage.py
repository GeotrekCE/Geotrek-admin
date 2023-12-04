import os.path

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point
from django.contrib.gis.geos.error import GEOSException
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geotrek.authent.models import default_structure
from geotrek.authent.models import Structure
from geotrek.common.models import Organism
from geotrek.core.models import Topology
from geotrek.signage.models import Sealing, Signage, SignageType
from geotrek.infrastructure.models import InfrastructureCondition
from django.conf import settings


class Command(BaseCommand):
    help = 'Load a layer with point geometries in the structure model\n'
    can_import_settings = True
    counter = 0

    def add_arguments(self, parser):
        parser.add_argument('point_layer')
        parser.add_argument('--use-structure', action='store_true', dest='use_structure', default=False,
                            help='Allow to use structure for condition and type of infrastructures')
        parser.add_argument('--encoding', '-e', action='store', dest='encoding', default='utf-8',
                            help='File encoding, default utf-8')
        parser.add_argument('--name-field', '-n', action='store', dest='name_field', help='Name of the field that will be mapped to the Name field in Geotrek')
        parser.add_argument('--type-field', '-t', action='store', dest='type_field', help='Name of the field that will be mapped to the Type field in Geotrek')
        parser.add_argument('--condition-field', '-c', action='store', dest='condition_field', help='Name of the field that will be mapped to the Condition field in Geotrek')
        parser.add_argument('--manager-field', '-m', action='store', dest='manager_field', help='Name of the field that will be mapped to the Manager field in Geotrek')
        parser.add_argument('--sealing-field', action='store', dest='sealing_field', help='Name of the field that will be mapped to the sealing field in Geotrek')
        parser.add_argument('--structure-field', '-s', action='store', dest='structure_field', help='Name of the field that will be mapped to the Structure field in Geotrek')
        parser.add_argument('--description-field', '-d', action='store', dest='description_field', help='Name of the field that will be mapped to the Description field in Geotrek')
        parser.add_argument('--year-field', '-y', action='store', dest='year_field', help='Name of the field that will be mapped to the Year field in Geotrek')
        parser.add_argument('--code-field', action='store', dest='code_field', help='Name of the field that will be mapped to the Code field in Geotrek')
        parser.add_argument('--eid-field', action='store', dest='eid_field', help='Name of the field that will be mapped to the External ID in Geotrek')
        parser.add_argument('--type-default', action='store', dest='type_default', help='Default value for Type field')
        parser.add_argument('--name-default', action='store', dest='name_default', help='Default value for Name field')
        parser.add_argument('--condition-default', action='store', dest='condition_default', help='Default value for Condition field')
        parser.add_argument('--manager-default', action='store', dest='manager_default', help='Default value for the Manager field')
        parser.add_argument('--sealing-default', action='store', dest='sealing_default', help='Default value for the Sealing field')
        parser.add_argument('--structure-default', action='store', dest='structure_default', help='Default value for Structure field')
        parser.add_argument('--description-default', action='store', dest='description_default', default="",
                            help='Default value for Description field')
        parser.add_argument('--year-default', action='store', dest='year_default', help='Default value for Year field')
        parser.add_argument('--code-default', action='store', dest='code_default', default="", help='Default value for Code field')

    def check_fields_available_with_default(self, available_fields, name_field, default_field, prefix_argument):
        if (name_field and name_field not in available_fields) \
                or (not name_field and not default_field):
            self.stdout.write(self.style.ERROR(
                f"Field '{name_field}' not found in data source."))
            self.stdout.write(self.style.ERROR(
                f"Set it with --{prefix_argument}-field, or set a default value with --{prefix_argument}-default"))
            return False
        return True

    def check_fields_available_without_default(self, available_fields, name_field, prefix_argument):
        if name_field and name_field not in available_fields:
            self.stdout.write(self.style.ERROR(
                f"Field '{name_field}' not found in data source."))
            self.stdout.write(self.style.ERROR(
                f"Change your --{prefix_argument}-field option"))
            return False
        return True

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')

        filename = options['point_layer']

        if not os.path.exists(filename):
            raise CommandError('File does not exists at: %s' % filename)

        data_source = DataSource(filename, encoding=options.get('encoding'))

        use_structure = options.get('use_structure')
        field_name = options.get('name_field')
        default_name = options.get('name_default')
        field_infrastructure_type = options.get('type_field')
        default_infrastructure_type = options.get('type_default')
        field_condition_type = options.get('condition_field')
        default_condition_type = options.get('condition_default')
        field_manager = options.get('manager_field')
        default_manager = options.get('manager_default')
        field_sealing = options.get('sealing_field')
        default_sealing = options.get('default_sealing')
        field_structure_type = options.get('structure_field')
        field_description = options.get('description_field')
        default_description = options.get('description_default')
        field_implantation_year = options.get('year_field')
        default_year = options.get('year_default')
        field_code = options.get('code_field')
        default_code = options.get('code_default')
        field_eid = options.get('eid_field')

        sid = transaction.savepoint()
        structure_default = options.get('structure_default')

        try:
            for layer in data_source:
                available_fields = layer.fields
                if verbosity >= 2:
                    self.stdout.write("- Layer '{}' with {} objects found".format(layer.name, layer.num_feat))
                if not self.check_fields_available_with_default(available_fields, field_infrastructure_type,
                                                                default_infrastructure_type, 'type'):
                    break
                if not self.check_fields_available_with_default(available_fields, field_name, default_name, 'name'):
                    break
                if not self.check_fields_available_without_default(available_fields, field_condition_type, 'condition'):
                    break
                if not self.check_fields_available_without_default(available_fields, field_manager, 'manager'):
                    break
                if not self.check_fields_available_without_default(available_fields, field_sealing, 'sealing'):
                    break
                if not self.check_fields_available_without_default(available_fields, field_structure_type, 'structure'):
                    break
                elif not field_structure_type and not structure_default:
                    structure = default_structure()
                elif not field_structure_type and structure_default:
                    try:
                        structure = Structure.objects.get(name=structure_default)
                        if verbosity > 0:
                            self.stdout.write("Signages will be linked to {}".format(structure))
                    except Structure.DoesNotExist:
                        self.stdout.write("Structure {} set in options doesn't exist".format(structure_default))
                        break

                if not self.check_fields_available_without_default(available_fields, field_description, 'description'):
                    break
                if not self.check_fields_available_without_default(available_fields, field_implantation_year, 'year'):
                    break
                if not self.check_fields_available_without_default(available_fields, field_eid, 'eid'):
                    break
                if not self.check_fields_available_without_default(available_fields, field_code, 'code'):
                    break

                for feature in layer:
                    feature_geom = feature.geom
                    name = feature.get(field_name) if field_name in available_fields else default_name
                    if feature_geom.geom_type == 'MultiPoint':
                        self.stdout.write(self.style.NOTICE("This object is a MultiPoint : %s" % name))
                        if len(feature_geom) < 2:
                            feature_geom = feature_geom[0].geos
                        else:
                            raise CommandError("One of your geometry is a MultiPoint object with multiple points")

                    tmp_signage_type = feature.get(field_infrastructure_type) if field_infrastructure_type in available_fields else default_infrastructure_type
                    signage_type, created = SignageType.objects.get_or_create(label=tmp_signage_type, structure=structure if use_structure else None)
                    if created and verbosity:
                        self.stdout.write("- SignageType '{}' created".format(signage_type))

                    condition = feature.get(field_condition_type) if field_condition_type in available_fields else default_condition_type
                    if condition:
                        condition_type, created = InfrastructureCondition.objects.get_or_create(label=condition, structure=structure if use_structure else None)
                        if created and verbosity:
                            self.stdout.write("- Condition Type '{}' created".format(condition_type))
                    else:
                        condition_type = None

                    sealing = feature.get(field_sealing) if field_sealing in available_fields else default_sealing
                    if sealing:
                        sealing, created = Sealing.objects.get_or_create(label=sealing, structure=structure if use_structure else None)
                        if created and verbosity:
                            self.stdout.write("- Sealing '{}' created".format(sealing))
                    else:
                        sealing = None

                    manager = feature.get(field_manager) if field_manager in available_fields else default_manager
                    if manager:
                        manager, created = Organism.objects.get_or_create(organism=manager, structure=structure if use_structure else None)
                        if created and verbosity:
                            self.stdout.write("- Organism '{}' created".format(manager))
                    else:
                        manager = None

                    structure = Structure.objects.get(name=feature.get(field_structure_type)) if field_structure_type in available_fields else structure
                    description = feature.get(field_description) if field_description in available_fields else default_description

                    year = feature.get(field_implantation_year) if field_implantation_year in available_fields else default_year
                    if year:
                        if str(year).isdigit():
                            year = int(year)
                        else:
                            raise CommandError('Invalid year: "%s" is not a number.' % year)
                    else:
                        year = None

                    eid = feature.get(field_eid) if field_eid in available_fields else None
                    code = feature.get(field_code) if field_code in available_fields else default_code

                    fields_to_integrate = {
                        'type': signage_type,
                        'name': name,
                        'condition': condition_type,
                        'structure': structure,
                        'description': description,
                        'implantation_year': year,
                        'sealing': sealing,
                        'manager': manager,
                        'code': code,
                        'eid': eid
                    }
                    self.create_signage(feature_geom, fields_to_integrate, verbosity)

            transaction.savepoint_commit(sid)
            if verbosity >= 2:
                self.stdout.write(self.style.NOTICE("{} objects created.".format(self.counter)))

        except Exception:
            self.stdout.write(self.style.ERROR("An error occured, rolling back operations."))
            transaction.savepoint_rollback(sid)
            raise

    def create_signage(self, geometry, fields_to_integrate, verbosity):

        with transaction.atomic():
            if fields_to_integrate['eid']:
                eid = fields_to_integrate.pop('eid')
                infra, created = Signage.objects.update_or_create(
                    eid=eid,
                    defaults=fields_to_integrate
                )
                if verbosity > 0 and not created:
                    self.stdout.write("Update : %s with eid %s" % (fields_to_integrate['name'], eid))
            else:
                infra = Signage.objects.create(**fields_to_integrate)
        if settings.TREKKING_TOPOLOGY_ENABLED:
            try:
                geometry = geometry.transform(settings.API_SRID, clone=True)
                geometry.coord_dim = 2
                serialized = '{"lng": %s, "lat": %s}' % (geometry.x, geometry.y)
                topology = Topology.deserialize(serialized)
                infra.mutate(topology)
            except IndexError:
                raise GEOSException('Invalid Geometry type.')
        else:
            if geometry.geom_type != 'Point':
                raise GEOSException('Invalid Geometry type.')
            geometry = geometry.transform(settings.SRID, clone=True)
            infra.geom = Point(geometry.x, geometry.y)
            infra.save()
        self.counter += 1

        return infra
