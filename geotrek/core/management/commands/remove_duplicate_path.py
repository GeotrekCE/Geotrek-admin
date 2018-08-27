from django.core.management.base import BaseCommand
from django.db import connection

from geotrek.core.models import Path


class Command(BaseCommand):
    help = 'Remove all duplicate path (same geom).\n'
    help += 'Do not remove path with topology.'

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        cursor = connection.cursor()
        sqlquery = """
        SELECT DISTINCT t1.id, t2.id FROM l_t_troncon t1
         JOIN l_t_troncon t2 ON t1.id < t2.id AND ST_EQUALS(t1.geom, t2.geom) ORDER BY t1.id"""
        cursor.execute(sqlquery)
        list_topologies = cursor.fetchall()
        to_delete = []
        for path1_pk, path2_pk in list_topologies:
            path1 = Path.objects.get(pk=path1_pk)
            path2 = Path.objects.get(pk=path2_pk)
            if path1.topology_set.exists() and path2.topology_set.exists():
                continue
            elif path1.topology_set.exists():
                if path2 not in to_delete:
                    to_delete.append(path2)
            elif path2.topology_set.exists():
                if path1 not in to_delete:
                    to_delete.append(path1)
            else:
                if path2 not in to_delete:
                    to_delete.append(path2)
        if verbosity > 0:
            self.stdout.write("Delete duplicate paths: %s" % [str(path.name) for path in to_delete])
        for path in to_delete:
            path.delete()
