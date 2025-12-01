from django.urls import path
from . import views
from django.shortcuts import render
from .views import dummy_view

urlpatterns = [
    path('', views.home, name='home'),

    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('register/student/', views.register_student, name='register_student'),

    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),


    path("test/", lambda r: render(r, "accounts/test.html"))
]

urlpatterns = [
    path("", dummy_view, name="accounts-home"),
]