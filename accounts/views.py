from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import TeacherSignUpForm, StudentSignUpForm, LoginForm, ProfileForm
from .models import Teacher, Student


def home(request):
    return render(request, "home.html", {"home": True})


def send_activation_email(request, user):
    current_site = request.get_host()

    subject = "Подтверждение регистрации MathGen"

    message = render_to_string("accounts/email_confirm.html", {
        "user": user,
        "domain": current_site,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
    })

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )


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

            send_activation_email(request, user)

            return render(request, "accounts/check_email.html", {
                "email": user.email
            })
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

            send_activation_email(request, user)

            return render(request, "accounts/check_email.html", {
                "email": user.email
            })
    else:
        form = StudentSignUpForm()

    return render(request, "accounts/register_student.html", {"form": form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        if hasattr(user, "teacher"):
            user.teacher.email_confirmed = True
            user.teacher.save()

        login(request, user)
        messages.success(request, "Email успешно подтверждён. Добро пожаловать в MathGen.")
        return redirect("home")

    return render(request, "accounts/activation_invalid.html")

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
        "form": form
    })

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        for field in form.fields.values():
            field.widget.attrs.update({
                "class": "form-control rounded-3"
            })

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменён.")
            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)

        for field in form.fields.values():
            field.widget.attrs.update({
                "class": "form-control rounded-3"
            })

    return render(request, "accounts/change_password.html", {
        "form": form
    })