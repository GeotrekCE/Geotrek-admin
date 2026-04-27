import time

from django.core.management.base import BaseCommand

from geotrek.common.utils.generate_pmtiles import generate_pmtiles


class Command(BaseCommand):
    help = "Create pmtiles of the selected baselayer"

    def add_arguments(self, parser):
        parser.add_argument(
            "id",
            type=int,
            help="Baselayer id in MapBaselayer model",
        )
        parser.add_argument(
            "minzoom",
            nargs="?",
            default=None,
            type=int,
            help="Minimum zoom level",
        )
        parser.add_argument(
            "maxzoom",
            nargs="?",
            default=None,
            type=int,
            help="Maximum zoom level",
        )

    def handle(self, *args, **options):
        # mettre un commentaire disant que l'on prend toujours la première source
        baselayer_id = options["id"]
        minzoom = options["minzoom"]
        maxzoom = options["maxzoom"]

        start = time.perf_counter()

        self.stdout.write("Start generating pmtiles...")
        generate_pmtiles(baselayer_id, minzoom, maxzoom)
        self.stdout.write("PMTiles available")

        end = time.perf_counter()
        self.stdout.write(f"time: {end - start} seconds")
