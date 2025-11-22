from django.shortcuts import render
from django.http import FileResponse
from .utils import generate_pdf_from_tasks


def index(request):
    return render(request, "generator/index.html")


def generate_pdf(request):
    pdf_path = generate_pdf_from_tasks()
    return FileResponse(
        open(pdf_path, "rb"),
        content_type="application/pdf",
        filename="tasks.pdf",
        as_attachment=False   # ← ВАЖНО! открывать в браузере
    )
