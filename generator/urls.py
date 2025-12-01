# generator/urls.py
from django.urls import path
from . import views

app_name = "generator"

urlpatterns = [
    path("", views.index, name="index"),
    path("pdf/", views.generate_pdf, name="generate_pdf"),
]
