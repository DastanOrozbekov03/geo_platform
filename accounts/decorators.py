from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user

        if user.is_superuser or user.is_staff:
            return view_func(request, *args, **kwargs)

        if hasattr(user, "teacher"):
            return view_func(request, *args, **kwargs)

        return redirect("student_dashboard")

    return wrapper
