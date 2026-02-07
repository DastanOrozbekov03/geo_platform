from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("register/teacher/", views.register_teacher, name="register_teacher"),
    path("register/student/", views.register_student, name="register_student"),

    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
]
