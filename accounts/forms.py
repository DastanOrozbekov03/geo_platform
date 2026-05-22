from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control rounded-3"
            })

class TeacherSignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", required=False)
    last_name = forms.CharField(label="Фамилия", required=False)
    email = forms.EmailField(label="Email", required=True)
    school = forms.CharField(label="Школа", required=False)
    position = forms.CharField(label="Должность", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
            "class": "form-control rounded-3 border-0 bg-body-tertiary py-2",
            "style": "font-size:15px;"
        })

        self.fields["username"].widget.attrs.update({
            "placeholder": "teacher01"
        })
        self.fields["email"].widget.attrs.update({
            "placeholder": "teacher@mail.com"
        })
        self.fields["first_name"].widget.attrs.update({
            "placeholder": "Имя"
        })
        self.fields["last_name"].widget.attrs.update({
            "placeholder": "Фамилия"
        })
        self.fields["school"].widget.attrs.update({
            "placeholder": "Школа №12"
        })
        self.fields["position"].widget.attrs.update({
            "placeholder": "Учитель математики"
        })
        self.fields["password1"].widget.attrs.update({
            "placeholder": "Введите пароль"
        })
        self.fields["password2"].widget.attrs.update({
            "placeholder": "Повторите пароль"
        })

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    
class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", required=False)
    last_name = forms.CharField(label="Фамилия", required=False)
    email = forms.EmailField(label="Email", required=True)
    grade = forms.IntegerField(label="Класс", required=False, min_value=1, max_value=12)
    school = forms.CharField(label="Школа", required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите логин"
        })
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Введите пароль"
        })
    )