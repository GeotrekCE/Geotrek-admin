from django.core.management.base import BaseCommand

from geotrek.core.models import Path
from geotrek.core.path_router import PathRouter


class Command(BaseCommand):
    help = """
    Generates the paths graph (pgRouting network topology) by filling
    columns source and target of the core_path table.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            dest="flush",
            default=False,
            help="Clear existing graph data before regenerating. Without this option, only missing parts of the graph are generated. You have to use this option if you are regenerating the graph after modifying the PGROUTING_TOLERANCE parameter.",
        )

    def handle(self, *args, **options):
        flush = options.get("flush")
        if flush:
            Path.objects.all().update(source_pgr=None, target_pgr=None)
        PathRouter()  # PathRouter's init method builds the network topology
