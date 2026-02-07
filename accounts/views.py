from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import TeacherSignUpForm, StudentSignUpForm, LoginForm
from .models import Teacher, Student


# ------------------------------ HOME ------------------------------
def home(request):
    return render(request, "home.html", {"home": True})


# ------------------------------ TEACHER REGISTER ------------------------------
def register_teacher(request):
    if request.method == "POST":
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()

            Teacher.objects.create(
                user=user,
                school=form.cleaned_data.get("school", "")
            )

            login(request, user)
            return redirect("home")
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

            Student.objects.create(
                user=user,
                grade=form.cleaned_data.get("grade")
            )

            login(request, user)
            return redirect("home")
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
            return redirect("home")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


# ------------------------------ LOGOUT ------------------------------
@login_required
def user_logout(request):
    logout(request)
    return redirect("home")
