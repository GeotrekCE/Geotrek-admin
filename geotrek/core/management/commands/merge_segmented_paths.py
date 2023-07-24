import copy
from time import sleep

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from geotrek.core.models import Path


class Command(BaseCommand):
    help = 'Find and merge Paths that are splitted in several segments\n'

    def add_arguments(self, parser):
        parser.add_argument('--sleeptime', '-d', action='store', dest='sleeptime', default=0.25,
                            help="Time to wait between merges (SQL triggers take time)")

    def extract_neighbourgs_graph(self, number_of_neighbourgs, discarded=[]):
        # Get all neighbours for each path, identify paths that could be merged (2 neighbours only)
        neighbours = dict()
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
                    if path_id not in discarded and len(path_neighbours_ids) == number_of_neighbourgs:
                        neighbours[path_id] = path_neighbours_ids
        return neighbours

    def merge_paths_with_one_neighbour(self):
        print("┌ STEP 1")
        neighbours_graph = self.extract_neighbourgs_graph(1)
        successes = 0
        while len(neighbours_graph):
            for path, neighbours in neighbours_graph.items():
                neighbour = neighbours[0]
                patha = Path.include_invisible.get(pk=int(path))
                pathb = Path.include_invisible.get(pk=int(neighbour))
                success = patha.merge_path(pathb)
                if success == 2:
                    print(f"├ Cannot merge {path} and {neighbour}")
                elif success == 0:
                    print(f"├ No matching points to merge paths {path} and {neighbour} found")
                else:
                    print(f"├ Merged {neighbour} into {path}")
                    successes += 1
                    sleep(self.sleeptime)
            neighbours_graph = self.extract_neighbourgs_graph(1)
        return successes

    def merge_paths_with_two_neighbours(self):
        print("┌ STEP 2")
        extremities = []
        successes = 0
        neighbours_graph = self.extract_neighbourgs_graph(2)
        mergeables = neighbours_graph.keys()
        while len(mergeables) > 0:
            for (a, neighbours) in neighbours_graph.items():
                b = neighbours[0]
                patha = Path.include_invisible.get(pk=int(a))
                pathb = Path.include_invisible.get(pk=int(b))
                success = patha.merge_path(pathb)
                if success == 2:
                    print(f"├ Cannot merge {a} and {b}")
                    extremities.append(a)
                else:
                    print(f"├ Merged {b} into {a}")
                    successes += 1
                    sleep(self.sleeptime)
            neighbours_graph = self.extract_neighbourgs_graph(2, discarded=extremities)
            mergeables = neighbours_graph.keys()
        return successes

    def merge_paths_with_three_neighbours(self):
        print("┌ STEP 3")
        extremities = []
        successes = 0
        neighbours_graph = self.extract_neighbourgs_graph(3)
        mergeables = list(neighbours_graph.keys())
        while len(mergeables) > 0:
            still_mergeables = copy.deepcopy(mergeables)
            for (a, neighbours) in neighbours_graph.items():
                if a in still_mergeables:
                    b = neighbours[0]
                    patha = Path.include_invisible.get(pk=int(a))
                    pathb = Path.include_invisible.get(pk=int(b))
                    success = patha.merge_path(pathb)
                    if success == 2:
                        print(f"├ Cannot merge {a} and {b}")
                        b = neighbours[1]
                        patha = Path.include_invisible.get(pk=int(a))
                        pathb = Path.include_invisible.get(pk=int(b))
                        success = patha.merge_path(pathb)
                        if success == 2:
                            print(f"├ Cannot merge {a} and {b}")
                            b = neighbours[2]
                            patha = Path.include_invisible.get(pk=int(a))
                            pathb = Path.include_invisible.get(pk=int(b))
                            success = patha.merge_path(pathb)
                            if success == 2:
                                print(f"├ Cannot merge {a} and {b}")
                                extremities.append(a)
                            else:
                                print(f"├ Merged {b} into {a}")
                                sleep(self.sleeptime)
                                still_mergeables.remove(b)
                                successes += 1
                        else:
                            print(f"├ Merged {b} into {a}")
                            sleep(self.sleeptime)
                            still_mergeables.remove(b)
                            successes += 1
                    else:
                        print(f"├ Merged {b} into {a}")
                        sleep(self.sleeptime)
                        still_mergeables.remove(b)
                        successes += 1
            neighbours_graph = self.extract_neighbourgs_graph(3, discarded=extremities)
            mergeables = list(neighbours_graph.keys())
        return successes

    def handle(self, *args, **options):
        self.sleeptime = options.get('sleeptime')
        # Mettre un warning et un sleep
        total_successes = 0
        print("\n")
        first_step_successes = self.merge_paths_with_one_neighbour()
        print(f"└ {first_step_successes} merges")
        total_successes += first_step_successes
        second_step_successes = self.merge_paths_with_two_neighbours()
        print(f"└ {second_step_successes} merges")
        total_successes += second_step_successes
        third_step_successes = self.merge_paths_with_three_neighbours()
        print(f"└ {third_step_successes} merges")
        total_successes += third_step_successes
        merges_string = "MERGED " + str(total_successes) + " PATHS"
        print(f"\n{merges_string:-^20}")
