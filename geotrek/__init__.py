import os

root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

#: Module version, as defined in PEP-0396.
__version__ = open(os.path.join(root, 'VERSION')).read().strip()
