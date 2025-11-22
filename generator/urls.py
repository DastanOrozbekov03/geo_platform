from django.urls import path
from .views import index, generate_pdf

urlpatterns = [
    path("", index, name="generator_index"),
    path("pdf/", generate_pdf, name="generate_pdf"),
]
