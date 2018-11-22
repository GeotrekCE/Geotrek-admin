import os

here = os.path.abspath(os.path.dirname(__file__))

__version__ = open(os.path.join(os.path.dirname(here), 'VERSION')).read().strip()
