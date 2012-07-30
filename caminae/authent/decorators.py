from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import available_attrs

__all__ = ('path_manager_required',
           'trekking_manager_required',
           'editor_required',
           'administrator_required',)


def user_passes_test_or_redirect(f, redirect_to, msg):
    """
    Check if a user has expected group membership.
    """
    # TODO : why not django's user_pass_test(f, login_url=url) decorator ?
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if f(request.user):
                return view_func(request, *args, **kwargs)
            messages.warning(request, msg)
            return redirect(redirect_to, *args, **kwargs)
        return _wrapped_view
    return decorator


def path_manager_required(redirect_to):
    # TODO : decorate wrapped fonction with login_required instead of testing is_authenticated
    f = lambda u: u.is_authenticated() and u.profile.is_path_manager()
    m = _(u'Access to the requested resource is restricted to path managers. You have been redirected.')
    return user_passes_test_or_redirect(f, redirect_to, m)


def trekking_manager_required(redirect_to):
    f = lambda u: u.is_authenticated() and u.profile.is_comm_manager()
    m = _(u'Access to the requested resource is restricted to communication managers. You have been redirected.')
    return user_passes_test_or_redirect(f, redirect_to, m)


def editor_required(redirect_to):
    f = lambda u: u.is_authenticated() and u.profile.is_editor()
    m = _(u'Access to the requested resource is restricted to work editor. You have been redirected.')
    return user_passes_test_or_redirect(f, redirect_to, m)


def admininistrator_required(redirect_to):
    f = lambda u: u.is_authenticated() and u.profile.is_administrator()
    m = _(u'Access to the requested resource is restricted to administrator. You have been redirected.')
    return user_passes_test_or_redirect(f, redirect_to, m)


def same_structure_required(redirect_to):
    """
    A decorator for class-based views. It relies on ``self.get_object()``
    method object, and assumes decorated views to handle ``StructureRelated``
    objects.
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(self, request, *args, **kwargs):
            result = view_func(self, request, *args, **kwargs)
            obj = self.get_object()
            if obj.same_structure(request.user):
                return result
            messages.warning(request, _(u'Access to the requested resource is restricted by structure. You have been redirected.'))
            return redirect(redirect_to, *args, **kwargs)
        return _wrapped_view
    return decorator
