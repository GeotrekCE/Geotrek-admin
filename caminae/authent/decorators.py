from functools import wraps
from django.shortcuts import redirect
from django.utils.decorators import available_attrs

__all__ = ('path_manager_required',
           'comm_manager_required',
           'editor_required',
           'administrator_required',)


def user_passes_test_or_redirect(f, redirect_to):
    """
    Check if a user has expected group membership.
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if f(request.user):
                return view_func(request, *args, **kwargs)
            return redirect(redirect_to, *args, **kwargs)
        return _wrapped_view
    return decorator


def path_manager_required(redirect_to):
    f = lambda u: u.is_authenticated() and u.profile.is_path_manager()
    return user_passes_test_or_redirect(f, redirect_to=redirect_to)


def comm_manager_required(redirect_to):
    f = lambda u: u.is_authenticated() and u.profile.is_comm_manager()
    return user_passes_test_or_redirect(f, redirect_to=redirect_to)


def editor_required(redirect_to):
    f = lambda u: u.is_authenticated() and u.profile.is_editor()
    return user_passes_test_or_redirect(f, redirect_to=redirect_to)


def admininistrator_required(redirect_to):
    f = lambda u: u.is_authenticated() and u.profile.is_administrator()
    return user_passes_test_or_redirect(f, redirect_to=redirect_to)
