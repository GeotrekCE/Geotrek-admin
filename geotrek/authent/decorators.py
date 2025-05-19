from functools import wraps

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


def same_structure_required(redirect_to):
    """
    A decorator for class-based views. It relies on ``self.get_object()``
    method object, and assumes decorated views to handle ``StructureRelated``
    objects.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            result = view_func(self, request, *args, **kwargs)

            if isinstance(result, HttpResponseRedirect):
                return result

            obj = (hasattr(self, "get_object") and self.get_object()) or getattr(
                self, "object", None
            )
            if obj.same_structure(request.user):
                return result
            messages.warning(
                request,
                _(
                    "Access to the requested resource is restricted by structure. You have been redirected."
                ),
            )

            return redirect(redirect_to, *args, **kwargs)

        return _wrapped_view

    return decorator
