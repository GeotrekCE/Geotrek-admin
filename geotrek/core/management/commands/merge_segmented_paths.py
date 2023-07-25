from datetime import datetime
from time import sleep

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from geotrek.core.models import Path


class Command(BaseCommand):
    help = 'Find and merge Paths that are splitted in several segments\n'

    def add_arguments(self, parser):
        parser.add_argument('--sleeptime', '-d', action='store', dest='sleeptime', default=0.25,
                            help="Time to wait between merges (SQL triggers take time)")

    def extract_neighbourgs_graph(self, number_of_neighbourgs, extremities=[]):
        # Get all neighbours for each path
        neighbours = dict()
        with connection.cursor() as cursor:
            cursor.execute('''select id1, array_agg(id2) from
                        (select p1.id as id1, p2.id as id2
                        from core_path p1, core_path p2
                        where st_touches(p1.geom, p2.geom) and (p1.id != p2.id)
                        group by p1.id, p2.id
                        order by p1.id) a
                        group by id1;''')

            for path_id, path_neighbours_ids in cursor.fetchall():
                if path_id not in extremities and len(path_neighbours_ids) == number_of_neighbourgs:
                    neighbours[path_id] = path_neighbours_ids
        return neighbours

    def try_merge(self, a, b):
        if {a, b} in self.discarded:
            print(f"├ Already discarded {a} and {b}")
            return False
        try:
            patha = Path.include_invisible.get(pk=a)
            pathb = Path.include_invisible.get(pk=b)
            with transaction.atomic():
                success = patha.merge_path(pathb)
                if success == 2:
                    print(f"├ Cannot merge {a} and {b}")
                    self.discarded.append({a, b})
                    return False
                elif success == 0:
                    print(f"├ No matching points to merge paths {a} and {b} found")
                    self.discarded.append({a, b})
                    return False
                else:
                    print(f"├ Merged {b} into {a}")
                    sleep(self.sleeptime)
                    return True
        except Exception:
            self.discarded.append({a, b})
            return False

    def merge_paths_with_one_neighbour(self):
        print("┌ STEP 1")
        neighbours_graph = self.extract_neighbourgs_graph(1)
        successes = 0
        fails = 0
        while len(neighbours_graph) > fails:
            fails = 0
            for path, neighbours in neighbours_graph.items():
                success = self.try_merge(path, neighbours[0])
                if success:
                    successes += 1
                else:
                    fails += 1
            neighbours_graph = self.extract_neighbourgs_graph(1)
        return successes

    def merge_paths_with_two_neighbours(self):
        print("┌ STEP 2")
        successes = 0
        neighbours_graph = self.extract_neighbourgs_graph(2)
        mergeables = list(neighbours_graph.keys())
        fails = 0
        while len(mergeables) > fails:
            fails = 0
            for (a, neighbours) in neighbours_graph.items():
                b = neighbours[0]
                success = self.try_merge(a, b)
                if success:
                    successes += 1
                else:
                    fails += 1
            neighbours_graph = self.extract_neighbourgs_graph(2)
            mergeables = neighbours_graph.keys()
        return successes

    def merge_paths_with_three_neighbours(self):
        print("┌ STEP 3")
        successes = 0
        neighbours_graph = self.extract_neighbourgs_graph(3)
        mergeables = list(neighbours_graph.keys())
        extremities = []
        while len(mergeables) > len(extremities):
            for (a, neighbours) in neighbours_graph.items():
                failed_neighbours = 0
                for n in neighbours:
                    success = self.try_merge(a, n)
                    if success:
                        successes += 1
                    else:
                        failed_neighbours += 1
                    if failed_neighbours == 3:
                        extremities.append(a)
            neighbours_graph = self.extract_neighbourgs_graph(3, extremities=extremities)
            mergeables = list(neighbours_graph.keys())
        return successes

    def handle(self, *args, **options):
        self.sleeptime = options.get('sleeptime')
        total_successes = 0
        self.discarded = []
        paths_before = Path.include_invisible.count()

        print("\n")
        print(datetime.now())

        first_step_successes = self.merge_paths_with_one_neighbour()
        print(f"└ {first_step_successes} merges")
        total_successes += first_step_successes

        second_step_successes = self.merge_paths_with_two_neighbours()
        print(f"└ {second_step_successes} merges")
        total_successes += second_step_successes

        third_step_successes = self.merge_paths_with_three_neighbours()
        print(f"└ {third_step_successes} merges")
        total_successes += third_step_successes

        paths_after = Path.include_invisible.count()
        print(f"\n--- RAN {total_successes} MERGES - FROM {paths_before} TO {paths_after} PATHS ---\n")
        print(datetime.now())
