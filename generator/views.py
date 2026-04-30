import os
import tempfile
from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from taskbank.models import Task
from taskbank.services import generate_task_instance
from .utils import latex_escape, MAX_TIME, compile_latex


def make_preview_list():
    preview = []

    tasks = (
        Task.objects.filter(is_active=True)
        .select_related("subject", "topic", "subtopic", "formula")
        .order_by("grade", "topic__name", "subtopic__name", "title")
    )

    for task in tasks:
        preview.append({
            "id": task.id,
            "title": task.title,
            "topic": task.topic.name if task.topic else "",
            "subtopic": task.subtopic.name if task.subtopic else "",
            "task": task.task_template,
            "description": f"{task.source} {task.source_number}".strip(),
            "level": task.difficulty,
            "time_minutes": task.time_minutes,
            "grade": task.grade,
            "task_type": task.task_type,
        })

    return preview


@login_required(login_url="login")
def index(request):
    preview = make_preview_list()

    all_topics = sorted({t["topic"] for t in preview if t["topic"]})
    all_subtopics = sorted({t["subtopic"] for t in preview if t["subtopic"]})

    return render(request, "generator/index.html", {
        "tasks": preview,
        "all_topics": all_topics,
        "all_subtopics": all_subtopics,
        "MAX_TIME": MAX_TIME,
    })


def _build_latex_document(task_objects, request_user, num_students, with_solutions):
    """
    task_objects -> queryset / list объектов Task из БД
    Для каждого ученика задачи генерируются заново.
    """
    school = getattr(request_user, "school_name", "Не указано")
    teacher_name = request_user.get_full_name() or request_user.username
    today = date.today().strftime("%d.%m.%Y")

    # Время считаем по самим объектам задач, а не по сгенерированным данным
    total_time = sum(int(getattr(task, "time_minutes", 10)) for task in task_objects)

    parts = [
        r"\documentclass[12pt]{article}",
        r"\usepackage{fontspec}",
        r"\setmainfont{Times New Roman}",
        r"\usepackage{geometry, graphicx, amsmath, amssymb, tikz}",
        r"\geometry{a4paper, margin=1in}",
        r"\begin{document}",
    ]

    for student_idx in range(1, num_students + 1):
        # Для КАЖДОГО ученика создаем новый набор задач
        student_tasks = [generate_task_instance(task) for task in task_objects]

        parts.extend([
            r"\begin{center}",
            r"\LARGE \textbf{Контрольная работа} \\[0.3em]",
            rf"{{\fontsize{{20}}{{16}}\selectfont \textbf{{Вариант №{student_idx}}}}}\\[0.3em]",
            r"\rule{\textwidth}{0.5pt}",
            r"\end{center}",
            "",
            r"\begin{flushright}",
            r"{\small",
            f"Учитель: {latex_escape(teacher_name)}\\\\[0.2em]",
            f"Школа: {latex_escape(school)}\\\\[0.2em]",
            f"Количество учеников: {num_students}\\\\[0.2em]",
            f"Дата: {today}\\\\[0.2em]",
            f"Общее время: {total_time} минут\\\\",
            r"}",
            r"\end{flushright}",
            "",
        ])

        for i, task_data in enumerate(student_tasks, start=1):
            task_text = task_data.get("task", "Задача недоступна")
            solution = task_data.get("solution", "")
            tikz = task_data.get("tikz", "")
            topic = task_data.get("topic", "")
            subtopic = task_data.get("subtopic", "")
            difficulty = task_data.get("difficulty", 1)
            time_minutes = task_data.get("time_minutes", 10)
            source = task_data.get("source", "")
            source_number = task_data.get("source_number", "")

            parts.extend([
                f"\\subsection*{{Задача {i}}}",
                f"\\textbf{{Тема:}} {latex_escape(topic)}\\\\",
            ])

            if subtopic:
                parts.append(f"\\textbf{{Подтема:}} {latex_escape(subtopic)}\\\\")

            parts.extend([
                f"\\textbf{{Сложность:}} {difficulty}\\\\",
                f"\\textbf{{Время:}} {time_minutes} минут\\\\[6pt]",
            ])

            if source or source_number:
                parts.append(
                    f"\\textbf{{Источник:}} {latex_escape(source)} {latex_escape(source_number)}\\\\[6pt]"
                )

            parts.extend([
                latex_escape(str(task_text)),
                "",
            ])

            if tikz:
                parts.extend([tikz, ""])

            if with_solutions and solution:
                parts.extend([
                    r"\textbf{Решение:}\\",
                    latex_escape(str(solution)),
                    "",
                ])

        if student_idx != num_students:
            parts.extend([r"\newpage", ""])

    parts.append(r"\end{document}")
    return "\n".join(parts)


@login_required(login_url="login")
@require_http_methods(["POST"])
def generate_pdf(request):
    if not hasattr(request.user, "teacher"):
        return HttpResponseForbidden("Генерация доступна только учителям")

    with_solutions = request.POST.get("with_solutions") == "on"

    try:
        num_students = int(request.POST.get("num_students", 1))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Некорректное количество учеников")

    if num_students < 1 or num_students > 100:
        return HttpResponseBadRequest("Количество учеников должно быть от 1 до 100")

    selected_ids = request.POST.getlist("selected_tasks")
    if not selected_ids:
        return HttpResponseBadRequest("Не выбраны задачи для генерации")

    try:
        selected_ids = [int(x) for x in selected_ids]
    except ValueError:
        return HttpResponseBadRequest("Некорректные ID задач")

    task_objects = (
        Task.objects.filter(id__in=selected_ids, is_active=True)
        .select_related("subject", "topic", "subtopic", "formula")
    )

    if not task_objects.exists():
        return HttpResponseBadRequest("Выбранные задачи не найдены")

    total_time = sum(int(getattr(task, "time_minutes", 10)) for task in task_objects)
    if total_time > MAX_TIME:
        return HttpResponseBadRequest(
            f"Ошибка: суммарное время задач {total_time} мин превышает лимит {MAX_TIME} мин."
        )

    temp_dir = tempfile.mkdtemp()
    tex_path = os.path.join(temp_dir, "document.tex")

    try:
        latex_content = _build_latex_document(
            task_objects=task_objects,
            request_user=request.user,
            num_students=num_students,
            with_solutions=with_solutions,
        )
    except Exception as e:
        return HttpResponse(f"Ошибка генерации задач: {e}", status=500)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)

    ok, log_text = compile_latex("document.tex", temp_dir)
    pdf_path = os.path.join(temp_dir, "document.pdf")

    if not ok or not os.path.exists(pdf_path):
        log_path = os.path.join(temp_dir, "document.log")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
                log_text = lf.read()

        return HttpResponse(f"Ошибка LaTeX:<pre>{log_text}</pre>", status=500)

    return FileResponse(
        open(pdf_path, "rb"),
        as_attachment=True,
        filename="exam.pdf",
    )