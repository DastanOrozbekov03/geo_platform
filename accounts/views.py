import random
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import TeacherSignUpForm, StudentSignUpForm, LoginForm, ProfileForm
from .models import Teacher, Student, EmailVerificationCode


def home(request):
    return render(request, "home.html", {"home": True})


def send_email_code(user):
    existing_code = EmailVerificationCode.objects.filter(user=user).first()

    if existing_code:
        diff = timezone.now() - existing_code.created_at
        if diff < timedelta(seconds=30):
            return False

    code = str(random.randint(100000, 999999))

    EmailVerificationCode.objects.update_or_create(
        user=user,
        defaults={
            "code": code,
            "created_at": timezone.now(),
        }
    )

    send_mail(
        subject="Код подтверждения MathGen",
        message=f"Ваш код подтверждения MathGen: {code}\n\nКод действует 10 минут.",
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return True


def register_teacher(request):
    if request.method == "POST":
        form = TeacherSignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data.get("first_name", "")
            user.last_name = form.cleaned_data.get("last_name", "")
            user.is_active = False
            user.save()

            Teacher.objects.create(
                user=user,
                school=form.cleaned_data.get("school", ""),
                position=form.cleaned_data.get("position", ""),
                email_confirmed=False,
            )

            request.session["verify_user_id"] = user.id
            send_email_code(user)

            return redirect("verify_email_code")
    else:
        form = TeacherSignUpForm()

    return render(request, "accounts/register_teacher.html", {"form": form})


def register_student(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data.get("first_name", "")
            user.last_name = form.cleaned_data.get("last_name", "")
            user.is_active = False
            user.save()

            Student.objects.create(
                user=user,
                grade=form.cleaned_data.get("grade"),
                school=form.cleaned_data.get("school", ""),
            )

            request.session["verify_user_id"] = user.id
            send_email_code(user)

            return redirect("verify_email_code")
    else:
        form = StudentSignUpForm()

    return render(request, "accounts/register_student.html", {"form": form})


def verify_email_code(request):
    user_id = request.session.get("verify_user_id")

    if not user_id:
        messages.error(request, "Сессия подтверждения не найдена.")
        return redirect("login")

    try:
        user = User.objects.get(id=user_id)
        email_code = user.email_code
    except Exception:
        messages.error(request, "Код подтверждения не найден.")
        return redirect("login")

    if request.method == "POST":
        code = request.POST.get("code", "").strip()

        if email_code.is_expired():
            email_code.delete()
            messages.error(request, "Код истёк. Нажмите «Отправить повторно».")
            return redirect("verify_email_code")

        if code == email_code.code:
            user.is_active = True
            user.save()

            if hasattr(user, "teacher"):
                user.teacher.email_confirmed = True
                user.teacher.save()

            email_code.delete()
            request.session.pop("verify_user_id", None)

            login(request, user)
            messages.success(request, "Email подтверждён. Добро пожаловать!")
            return redirect("home")

        messages.error(request, "Неверный код подтверждения.")

    return render(request, "accounts/verify_email_code.html", {
        "email": user.email,
    })


def resend_email_code(request):
    user_id = request.session.get("verify_user_id")

    if not user_id:
        messages.error(request, "Сессия подтверждения не найдена.")
        return redirect("login")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Пользователь не найден.")
        return redirect("login")

    sent = send_email_code(user)

    if sent:
        messages.success(request, "Новый код отправлен на почту.")
    else:
        messages.warning(request, "Повторно отправить код можно через 30 секунд.")

    return redirect("verify_email_code")


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Неверный логин/пароль или email ещё не подтверждён."
        )
        return super().form_invalid(form)


user_login = CustomLoginView.as_view()


@login_required
def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


@login_required
def profile_edit(request):
    form = ProfileForm(instance=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()

            if hasattr(request.user, "teacher"):
                request.user.teacher.school = request.POST.get("school")
                request.user.teacher.position = request.POST.get("position")
                request.user.teacher.save()

            messages.success(request, "Профиль обновлён.")
            return redirect("profile")

    return render(request, "accounts/profile_edit.html", {
        "form": form,
    })


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
    else:
        form = PasswordChangeForm(request.user)

    for field in form.fields.values():
        field.widget.attrs.update({
            "class": "form-control rounded-3"
        })

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Пароль успешно изменён.")
        return redirect("profile")

    return render(request, "accounts/change_password.html", {
        "form": form,
    })