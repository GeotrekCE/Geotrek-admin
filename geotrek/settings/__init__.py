
import os
import ConfigParser

from django.core.exceptions import ImproperlyConfigured


PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


empty = object()


class EnvIniReader(object):
    def __init__(self, path):
        self.default_section = 'settings'
        # read file
        self.path = path
        self.ini = ConfigParser.ConfigParser()
        self.ini.readfp(open(path))

    def get(self, name, default=empty, section=None, env=True):
        # Environment has precedence
        envname = name.upper()
        value = os.getenv(envname, empty)
        if env and value is not empty:
            return value
        # Then read from ini
        section = section or self.default_section
        try:
            return self.ini.get(section, name)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            pass
        # Nothing found, use default
        if default is not empty:
            return default
        raise ImproperlyConfigured('%s not found in section %s (%s)' % (name, section, self.path))
