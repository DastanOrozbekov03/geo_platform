from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import TeacherSignUpForm, StudentSignUpForm, LoginForm
from .models import Teacher, Student


# ------------------------------ HOME ------------------------------
def home(request):
    return render(request, "home.html")


# ------------------------------ TEACHER REGISTER ------------------------------
def register_teacher(request):
    if request.method == "POST":
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()

            # создаём профиль учителя
            Teacher.objects.create(
                user=user,
                school=form.cleaned_data.get('school', "")
            )

            login(request, user)
            return redirect("teacher_dashboard")
    else:
        form = TeacherSignUpForm()

    return render(request, "accounts/register_teacher.html", {"form": form})


# ------------------------------ STUDENT REGISTER ------------------------------
def register_student(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()

            # создаём профиль ученика
            Student.objects.create(
                user=user,
                grade=form.cleaned_data.get('grade')
            )

            login(request, user)
            return redirect("student_dashboard")
    else:
        form = StudentSignUpForm()

    return render(request, "accounts/register_student.html", {"form": form})


# ------------------------------ LOGIN ------------------------------
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # РЕДИРЕКТ ПО РОЛЯМ
            if hasattr(user, "teacher"):
                return redirect("teacher_dashboard")
            if hasattr(user, "student"):
                return redirect("student_dashboard")

            return redirect("home")

    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


# ------------------------------ LOGOUT ------------------------------
@login_required
def user_logout(request):
    logout(request)
    return redirect("home")


# ------------------------------ DASHBOARDS ------------------------------
@login_required
@user_passes_test(lambda u: hasattr(u, "teacher"))
def teacher_dashboard(request):
    return render(request, "accounts/teacher_dashboard.html")


@login_required
@user_passes_test(lambda u: hasattr(u, "student"))
def student_dashboard(request):
    return render(request, "accounts/student_dashboard.html")

def dummy_view(request):
    return redirect("generator:index")