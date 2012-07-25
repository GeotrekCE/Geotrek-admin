"""
Simply create a few paths to test the CRUD workflow by hand.
"""

from caminae.core.factories import PathFactory


class Setup(object):

    requires = ()

    def __init__(self, verbosity=0):
        pass

    def run(self):
        for x in range(10):
            PathFactory()

