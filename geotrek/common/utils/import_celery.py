import os
import importlib

from django.conf import settings

from geotrek.common.parsers import Parser

if 'geotrek.zoning' in settings.INSTALLED_APPS:
    import geotrek.zoning.parsers  # noqa
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    import geotrek.sensitivity.parsers  # noqa
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    import geotrek.trekking.parsers  # noqa
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    import geotrek.tourism.parsers  # noqa
if 'geotrek.feedback' in settings.INSTALLED_APPS:
    import geotrek.feedback.parsers  # noqa
if 'geotrek.infrastucture' in settings.INSTALLED_APPS:
    import geotrek.infrastucture.parsers  # noqa
if 'geotrek.infrastucture' in settings.INSTALLED_APPS:
    import geotrek.infrastucture.parsers  # noqa


def subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(subclasses(subclass))

    return all_subclasses


def create_tmp_destination(name):
    save_dir = os.path.join(settings.TMP_DIR, os.path.splitext(name)[0])
    if not os.path.exists(settings.TMP_DIR):
        os.mkdir(settings.TMP_DIR)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    return save_dir, os.path.join(save_dir, name)


parsers_module = None


def discover_available_parsers(request):
    global parsers_module
    choices = []
    choices_url = []

    if not parsers_module:
        module_path = os.path.join(settings.VAR_DIR, 'conf/parsers.py')
        spec = importlib.util.spec_from_file_location('parsers', module_path)
        parsers_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(parsers_module)
        except FileNotFoundError:
            pass

    classes = subclasses(Parser)
    for index, cls in enumerate(classes):
        if cls.__module__.startswith('parsers') or cls.__module__.startswith('geotrek'):
            lang = request.LANGUAGE_CODE
            label_lang = getattr(cls, f'label_{lang}', None)
            if label_lang:
                label = label_lang
            else:
                label = cls.label
            if not label or not cls.model:
                continue
            codename = '{}.import_{}'.format(cls.model._meta.app_label, cls.model._meta.model_name)
            if not request.user.has_perm(codename):
                continue
            if not getattr(cls, 'url', None) and not getattr(cls, 'base_url', None):
                choices.append((index, label))
            else:
                choices_url.append((index, label))

    choices = sorted(choices, key=lambda x: x[1])
    choices_url = sorted(choices_url, key=lambda x: x[1])

    return choices, choices_url, classes
