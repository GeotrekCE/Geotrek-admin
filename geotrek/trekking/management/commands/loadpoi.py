import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geotrek.core.models import Topology
from geotrek.trekking.models import POI, POIType


class Command(BaseCommand):
    help = "Load a layer with point geometries in a model\n"
    can_import_settings = True
    counter = 0

    def add_arguments(self, parser):
        parser.add_argument("point_layer")
        parser.add_argument(
            "--encoding",
            "-e",
            action="store",
            dest="encoding",
            default="utf-8",
            help="File encoding, default utf-8",
        )
        parser.add_argument(
            "--name-field",
            "-n",
            action="store",
            dest="name_field",
            help="Name of the field that contains the name attribute. Required or use --name-default instead.",
        )
        parser.add_argument(
            "--type-field",
            "-t",
            action="store",
            dest="type_field",
            help="Name of the field that contains the POI Type attribute. Required or use --type-default instead.",
        )
        parser.add_argument(
            "--description-field",
            "-d",
            action="store",
            dest="description_field",
            help="Name of the field that contains the description of the POI (optional)",
        )
        parser.add_argument(
            "--name-default",
            action="store",
            dest="name_default",
            help="Default value for POI name. Use only if --name-field is not set",
        )
        parser.add_argument(
            "--type-default",
            action="store",
            dest="type_default",
            help="Default value for POI Type. Use only if --type-field is not set",
        )

    def handle(self, *args, **options):
        filename = options["point_layer"]

        if not os.path.exists(filename):
            raise CommandError("File does not exists at: %s" % filename)

        data_source = DataSource(filename, encoding=options.get("encoding"))

        verbosity = options.get("verbosity")
        field_name = options.get("name_field")
        field_poitype = options.get("type_field")
        field_description = options.get("description_field")

        sid = transaction.savepoint()

        try:
            for layer in data_source:
                if verbosity >= 1:
                    self.stdout.write(
                        f"- Layer '{layer.name}' with {layer.num_feat} objects found"
                    )
                available_fields = layer.fields

                if (field_name and field_name not in available_fields) or (
                    not field_name and not options.get("name_default")
                ):
                    self.stdout.write(
                        self.style.ERROR(
                            f"Field '{field_name}' not found in data source."
                        )
                    )
                    self.stdout.write(
                        self.style.ERROR(
                            "Set it with --name-field, or set a default value with --name-default"
                        )
                    )
                    break
                if (field_poitype and field_poitype not in available_fields) or (
                    not field_poitype and not options.get("type_default")
                ):
                    self.stdout.write(
                        self.style.ERROR(
                            f"Field '{field_poitype}' not found in data source."
                        )
                    )
                    self.stdout.write(
                        self.style.ERROR(
                            "Set it with --type-field, or set a default value with --type-default"
                        )
                    )
                    break

                for feature in layer:
                    feature_geom = feature.geom
                    name = (
                        feature.get(field_name)
                        if field_name in available_fields
                        else options.get("name_default")
                    )
                    poitype = (
                        feature.get(field_poitype)
                        if field_poitype in available_fields
                        else options.get("type_default")
                    )
                    description = (
                        feature.get(field_description)
                        if field_description in available_fields
                        else ""
                    )
                    self.create_poi(feature_geom, name, poitype, description)
                    if verbosity >= 2:
                        self.stdout.write(
                            self.style.NOTICE(f"{name} POI created.")
                        )

            transaction.savepoint_commit(sid)
            if verbosity >= 2:
                self.stdout.write(
                    self.style.NOTICE(f"{self.counter} objects created.")
                )

        except Exception:
            self.stdout.write(
                self.style.ERROR("An error occured, rolling back operations.")
            )
            transaction.savepoint_rollback(sid)
            raise

    def create_poi(self, geometry, name, poitype, description):
        poitype, created = POIType.objects.get_or_create(label=poitype)
        poi = POI.objects.create(name=name, type=poitype, description=description)
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Use existing topology helpers to transform a Point(x, y)
            # to a path aggregation (topology)
            geometry = geometry.transform(settings.API_SRID, clone=True)
            geometry.coord_dim = 2
            serialized = '{"lng": %s, "lat": %s}' % (geometry.x, geometry.y)
            topology = Topology.deserialize(serialized)
            # Move deserialization aggregations to the POI
            poi.mutate(topology)
        else:
            if geometry.geom_type != "Point":
                raise TypeError
            poi.geom = Point(geometry.x, geometry.y, srid=settings.SRID)
            poi.save()
        self.counter += 1

        return poi
