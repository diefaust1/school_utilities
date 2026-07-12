from functools import wraps

from django.http import HttpResponseForbidden

from .models import User


def can_use_teacher_tools(user: User) -> bool:
    return user.is_authenticated and user.role == User.Role.TEACHER


def teacher_action_required(message: str):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not can_use_teacher_tools(request.user):
                return HttpResponseForbidden(message)
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


def account_capabilities(request):
    return {
        "can_use_teacher_tools": can_use_teacher_tools(request.user),
    }
