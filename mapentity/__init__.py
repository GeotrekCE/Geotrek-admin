import re
import inspect
from collections import namedtuple, OrderedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.views.generic.base import View
from django.conf.urls import patterns

__all__ = ['app_settings', 'registry']


app_settings = dict({
    'TITLE': "",
    'HISTORY_ITEMS_MAX': 5,
    'CONVERSION_SERVER': '',
    'LANGUAGES': settings.LANGUAGES,
    'LANGUAGE_CODE': settings.LANGUAGE_CODE,
    'TEMP_DIR': getattr(settings, 'TEMP_DIR', '/tmp'),
}, **getattr(settings, 'MAPENTITY_CONFIG', {}))


MapEntity = namedtuple('MapEntity', ['menu', 'label', 'icon', 'icon_small', 'modelname', 'url_list'])


class Registry(object):
    def __init__(self):
        self.registry = OrderedDict()
        self.apps = {}

    def register(self, model, name='', menu=True):
        """ Register model and returns URL patterns
        """
        from .urlizor import view_classes_to_url

        # Ignore models from not installed apps
        if not model._meta.installed:
            return ()
        # Register once only
        if model in self.registry:
            return ()
        # Obtain app's views module from Model
        views_module_name = re.sub('models.*', 'views', model.__module__)
        views_module = import_module(views_module_name)
        # Filter to views inherited from MapEntity base views
        picked = []
        for name, view in inspect.getmembers(views_module):
            if inspect.isclass(view) and issubclass(view, View):
                if hasattr(view, 'get_entity_kind'):
                    try:
                        view_model = view.model or view.queryset.model
                    except AttributeError:
                        pass
                    else:
                        if view_model is model:
                            picked.append(view)

        module_name = model._meta.module_name
        app_label = model._meta.app_label

        mapentity = MapEntity(label=model._meta.verbose_name_plural,
                              modelname=module_name,
                              icon='images/%s.png' % module_name,
                              icon_small='images/%s-16.png' % module_name,
                              menu=menu,
                              url_list='%s:%s_%s' % (app_label, module_name, 'list'))

        self.registry[model] = mapentity
        # Returns Django URL patterns
        return patterns(name, *view_classes_to_url(*picked))

    @property
    def entities(self):
        return self.registry.values()


registry = Registry()
