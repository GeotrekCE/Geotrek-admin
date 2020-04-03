import os

here = os.path.abspath(os.path.dirname(__file__))

__version__ = open(os.path.join(here, 'VERSION')).read().strip()
