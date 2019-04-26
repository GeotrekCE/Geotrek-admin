from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from geotrek.core.models import Path


class Command(BaseCommand):
    help = """Remove all duplicate path (same geom)."""
    """Do not remove path with topology."""

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        cursor = connection.cursor()
        query = """with relations as (SELECT t1.id as t1_id,
                                             t2.id as t2_id
                                      FROM l_t_troncon t1
                                      JOIN l_t_troncon t2 ON t1.id < t2.id AND ST_OrderingEquals(t1.geom, t2.geom)
                                      ORDER BY t1.id, t2.id)
                      SELECT * FROM relations WHERE t1_id NOT IN (SELECT t2_id FROM relations) """
        cursor.execute(query)
        list_topologies = cursor.fetchall()

        path_deleted = []

        with transaction.atomic():
            try:
                for path1_pk, path2_pk in list_topologies:
                    path2 = Path.include_invisible.get(pk=path2_pk)
                    path2.aggregations.update(path_id=path1_pk)
                    path_deleted.append(path2)
                    if verbosity > 1:
                        self.stdout.write("Deleting path %s" % path2)
                    path2.delete()

            except Exception as exc:
                self.stdout.write(self.style.ERROR("{}".format(exc)))

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("{} duplicate paths have been deleted".format(len(path_deleted))))
