from django.http import HttpResponseForbidden
from functools import wraps

from django.shortcuts import redirect

from django.http import HttpResponseForbidden
from functools import wraps


def no_cache(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response

    return _wrapped_view


def user_type_required(user_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("index")  # Redirect to login page if not authenticated
            if getattr(request.user, "user_type", None) != user_type:
                return HttpResponseForbidden(
                    "You do not have permission to view this page."
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
