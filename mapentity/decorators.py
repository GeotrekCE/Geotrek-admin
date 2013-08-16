from functools import wraps
from collections import namedtuple

from django.utils.decorators import available_attrs

from . import app_settings


HistoryItem = namedtuple('HistoryItem', ['title', 'path', 'modelname'])


def save_history():
    """
    A decorator for class-based views, which save navigation history in
    session.
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(self, request, *args, **kwargs):
            result = view_func(self, request, *args, **kwargs)
            
            # Stack list of request paths
            history = request.session.get('history', [])
            # Remove previous visits of this page
            try:
                history = [h for h in history if h.path != request.path]
            except AttributeError:
                pass  # Manage legacy history items, which were simple tuples
            # Add this one and remove extras
            model = self.model or self.queryset.model
            history.insert(0, HistoryItem(unicode(self.get_title()), 
                                          request.path,
                                          unicode(model._meta.object_name.lower())))
            if len(history) > app_settings['HISTORY_ITEMS_MAX']:
                history.pop()
            request.session['history'] = history
            
            return result
        return _wrapped_view
    return decorator
