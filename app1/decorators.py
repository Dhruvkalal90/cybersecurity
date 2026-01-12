from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

def role_required(required_role,url):
    """
    Decorator to restrict a view to users with a specific role.
    Example: @role_required("hacker")
    """

    def decorator(view_func):
        @login_required(login_url='/login/')
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = request.user.role.name.lower() if request.user.role else ""

            if user_role == required_role.lower():
                return view_func(request, *args, **kwargs)

            return redirect(url)  # unauthorized → redirect to home

        return wrapper
    return decorator
