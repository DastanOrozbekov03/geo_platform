from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class TeacherSignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", required=False)
    last_name = forms.CharField(label="Фамилия", required=False)
    school = forms.CharField(label="Школа", required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", required=False)
    last_name = forms.CharField(label="Фамилия", required=False)
    grade = forms.IntegerField(label="Класс", required=False, min_value=1, max_value=12)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
