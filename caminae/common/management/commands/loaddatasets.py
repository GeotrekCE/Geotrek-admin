"""
Load a specific dataset into the database from caminae.common.datasets directory
"""

from django.core.management import base
from django.db import transaction
from django.utils import importlib


class Command(base.BaseCommand):
    args = '<dataset_name dataset_name ...>'
    help = 'Load a specific dataset into the database.'

    def handle(self, *dataset_names, **options):
        if not dataset_names:
            raise ValueError("At least one dataset name must be provided.")
        for name in dataset_names:
            self.load(name, **options)

    def load(self, dataset_name, **options):
        """Loads a dataset."""
        verbosity = options.get('verbosity', 0)
        indent = options.pop('indent', '')

        if verbosity > 0:
            self.stdout.write('%sImporting dataset %s...\n' % (indent, dataset_name))

        dataset = importlib.import_module('caminae.common.datasets.%s' % dataset_name)
        setup = dataset.Setup(verbosity=verbosity, indent=indent)

        # Handle required datasets
        for required in setup.requires:
            self.load(required, indent=indent + '  ', **options)

        # Load the data
        with transaction.commit_on_success():
            setup.run()

        if verbosity > 0:
            self.stdout.write('%sDone.\n' % indent)
