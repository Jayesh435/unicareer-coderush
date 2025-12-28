from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator to restrict view to admin users only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect('login')
        
        if request.user.role != 'admin':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """Decorator to restrict view to student users only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect('login')
        
        if request.user.role != 'student':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper
