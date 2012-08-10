"""
Simply create a few paths to test the CRUD workflow by hand.
"""

from . import BaseSetup

from caminae.core.factories import PathFactory


class Setup(BaseSetup):

    def run(self):
        for x in range(10):
            PathFactory()

