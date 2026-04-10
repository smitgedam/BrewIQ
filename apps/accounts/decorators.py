from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            try:
                profile = request.user.profile
                if profile.role in roles or request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
            except Exception:
                pass
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('orders:dashboard')
        return wrapper
    return decorator
