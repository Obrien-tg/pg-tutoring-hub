from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404


def teacher_required(view_func):
    """Decorator to require teacher permissions"""

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_teacher:
            raise PermissionDenied("Teacher access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def student_required(view_func):
    """Decorator to require student permissions"""

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_student:
            raise PermissionDenied("Student access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def parent_required(view_func):
    """Decorator to require parent permissions"""

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_parent:
            raise PermissionDenied("Parent access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def user_type_required(*allowed_types):
    """Decorator to require specific user types"""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.user_type not in allowed_types:
                raise PermissionDenied(
                    f"Access denied. Required user types: {', '.join(allowed_types)}"
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def own_profile_or_teacher_required(view_func):
    """Allow access to own profile or if user is teacher"""

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # If viewing own profile or user is teacher, allow access
        target_user_id = kwargs.get("user_id") or kwargs.get("pk")
        if target_user_id:
            if request.user.id == int(target_user_id) or request.user.is_teacher:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("You can only view your own profile.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
