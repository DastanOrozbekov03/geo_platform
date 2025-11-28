from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, "teacher"):
            return view_func(request, *args, **kwargs)
        # если ученик — кидаем его на панель ученика
        return redirect("student_dashboard")
    return wrapper
