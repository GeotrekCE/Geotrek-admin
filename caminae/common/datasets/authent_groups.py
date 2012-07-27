from . import BaseSetup

from caminae.authent.pyfixtures import populate_groups


class Setup(BaseSetup):

    def run(self):
        groups = populate_groups()
        if self.verbosity > 1:
            for group in groups.values():
                self.print_indent("Get or create group: %s" % group)



