from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import available_attrs

__all__ = ('path_manager_required',
           'comm_manager_required',
           'editor_required',
           'administrator_required',)


def user_passes_test_or_redirect(f, redirect_to, msg):
    """
    Check if a user has expected group membership.
    """
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
    f = lambda u: u.is_authenticated() and u.profile.is_path_manager()
    m = _(u'Access to the requested resource is restricted to path managers. You have been redirected.')
    return user_passes_test_or_redirect(f, redirect_to, m)


def comm_manager_required(redirect_to):
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
