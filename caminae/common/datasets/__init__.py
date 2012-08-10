import datetime

class BaseSetup(object):

    requires = ()

    def __init__(self, verbosity=0, now=None, indent="", **kwargs):
        self.verbosity = verbosity
        if now is None:
            now = datetime.datetime.now()

        self.kwargs = kwargs
        self.now = now
        self.indent = indent

    def run(self):
        raise NotImplementedError

    def print_indent(self, msg):
        print(self.indent + msg)

