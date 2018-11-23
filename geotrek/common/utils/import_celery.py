import os
import importlib

from django.conf import settings

from geotrek.common.parsers import Parser
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    import geotrek.sensitivity.parsers  # noqa


def subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(subclasses(subclass))

    return all_subclasses


def create_tmp_destination(name):
    save_dir = '/tmp/geotrek/{}'.format(name)
    if not os.path.exists('/tmp/geotrek'):
        os.mkdir('/tmp/geotrek')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    return save_dir, '/'.join((save_dir, name))


def discover_available_parsers(user):
    choices = []
    choices_url = []
    try:
        importlib.import_module('bulkimport.parsers')
    except ImportError:
        pass

    classes = subclasses(Parser)
    for index, cls in enumerate(classes):
        if cls.__module__.startswith('bulkimport') or cls.__module__.startswith('geotrek'):
            if not cls.label or not cls.model:
                continue
            codename = '{}.import_{}'.format(cls.model._meta.app_label, cls.model._meta.model_name)
            if not user.is_superuser and not user.has_perm(codename):
                continue
            if not getattr(cls, 'url', None) and not getattr(cls, 'base_url', None):
                choices.append((index, cls.label))
            else:
                choices_url.append((index, cls.label))

    choices = sorted(choices, key=lambda x: x[1])
    choices_url = sorted(choices_url, key=lambda x: x[1])

    return choices, choices_url, classes
