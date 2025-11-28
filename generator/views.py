from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from tasks.tasks import get_tasks_list
from .utils import generate_pdf_from_tasks
from accounts.decorators import teacher_required

@teacher_required
def index(request):
    tasks = get_tasks_list()
    return render(request, "generator/index.html", {"tasks": tasks})

@teacher_required
def generate_pdf(request):
    if request.method == "POST":

        selected_ids = [int(x) for x in request.POST.getlist("selected_tasks")]
        all_tasks = get_tasks_list()

        selected_tasks = [t for t in all_tasks if t["id"] in selected_ids]

        # лимит 45 минут
        total_time = sum(t["time_minutes"] for t in selected_tasks)
        if total_time > 45:
            return HttpResponse(
                f"<h2>⛔ Контрольная превышает лимит!</h2>"
                f"<p>Общее время: <b>{total_time} минут</b></p>"
                f"<p>Максимум: <b>45 минут</b></p>"
                f"<p>Уберите часть задач и попробуйте снова.</p>"
            )

        with_solutions = "with_solutions" in request.POST

        pdf_path = generate_pdf_from_tasks(selected_tasks, with_solutions)

        return FileResponse(open(pdf_path, "rb"),
                            content_type="application/pdf",
                            filename="tasks.pdf")

