import copy
from time import sleep

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from geotrek.core.models import Path


class Command(BaseCommand):
    help = 'Find and merge Paths that are splitted in several segments\n'

    def add_arguments(self, parser):
        parser.add_argument('--dry', '-d', action='store_true', dest='dry', default=False,
                            help="Do not change the database, dry run. Show the number of potential merges")

    def handle(self, *args, **options):
        dry = options.get('dry')

        # Get all neighbours for each path, identify paths that could be merged (2 neighbours only)
        neighbours = dict()
        mergeables = []
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute('''select id1, array_agg(id2) from
                            (select p1.id as id1, p2.id as id2
                            from core_path p1, core_path p2
                            where st_touches(p1.geom, p2.geom) and (p1.id != p2.id)
                            group by p1.id, p2.id
                            order by p1.id) a
                            group by id1;''')

                for path_id, path_neighbours_ids in cursor.fetchall():
                    if len(path_neighbours_ids) == 2:
                        mergeables.append(path_id)
                        neighbours[path_id] = path_neighbours_ids

        # Match couples of paths to merge together (first neighbour, if not matched with another path yet)
        still_mergeables = copy.deepcopy(mergeables)
        merges = 0
        merges_couples = []
        merges_in = []
        merges_out = []
        merges_flat = []
        for i in mergeables:
            if i in still_mergeables:
                neighbour = neighbours.get(i, None)
                if neighbour:
                    first_neighbour = neighbour[0]
                    if first_neighbour in still_mergeables:
                        merges += 1
                        merges_couples.append((i, first_neighbour))
                        merges_flat.append(i)
                        merges_flat.append(first_neighbour)
                        merges_in.append(i)
                        merges_out.append(first_neighbour)
                        still_mergeables.remove(i)
                        still_mergeables.remove(first_neighbour)

        algo_ok = set(merges_in).isdisjoint(set(merges_out))

        print(f"Found {merges} potential merges")

        if algo_ok and not dry:
            successes = 0
            fails = 0
            for (a, b) in merges_couples:
                patha = Path.include_invisible.get(pk=int(a))
                pathb = Path.include_invisible.get(pk=int(b))
                success = patha.merge_path(pathb)
                if success == 2:
                    print(f"3rd path in intersection of {a} and {b}")
                    fails += 1
                elif success == 0:
                    print(f"No matching points to merge paths {a} and {b} found")
                    fails += 1
                else:
                    print(f"Merged {b} into {a}")
                    successes += 1
                sleep(0.5)

            print(f"{successes} successful merges - {fails} failed merges")
