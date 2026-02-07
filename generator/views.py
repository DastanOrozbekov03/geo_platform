import os
import tempfile
from datetime import date
from django.shortcuts import render
from django.http import FileResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from tasks.tasks import get_tasks_list
from .utils import latex_escape, LEVEL_TIME, MAX_TIME, compile_latex


def make_preview_list():
    preview = []
    uid = 1

    for tmpl in get_tasks_list():
        # текст задачи для глазка
        task_text = tmpl.task_template  # оставляем шаблон
        # вместо конкретных чисел добавляем пояснение
        task_text_for_preview = task_text
        if hasattr(tmpl, "params") and tmpl.params:
            task_text_for_preview 



        preview.append({
            "id": uid,
            "template_id": tmpl.id,
            "topic": tmpl.topic,
            "text": task_text_for_preview,   # для глазка
            "task": task_text_for_preview,   # для глазка
            "solution": tmpl.solution_template,  # решение можно пока шаблонное
            "description": tmpl.source,
            "level": tmpl.level,
            "time_minutes": tmpl.time_minutes or LEVEL_TIME.get(tmpl.level, 10),
        })
        uid += 1

    return preview


@login_required(login_url="login")
def index(request):
    preview = make_preview_list()
    request.session["preview_tasks"] = preview
    request.session.modified = True
    all_topics = sorted({t["topic"] for t in preview})
    return render(request, "generator/index.html", {
        "tasks": preview,
        "all_topics": all_topics,
    })


@login_required(login_url="login")
@require_http_methods(["POST"])
def generate_pdf(request):
    selected = request.POST.getlist("selected_tasks")
    with_solutions = request.POST.get("with_solutions") == "on"
    num_students = int(request.POST.get("num_students", 1))

    preview = request.session.get("preview_tasks", [])
    if selected:
        try:
            selected_ids = {int(x) for x in selected}
        except:
            selected_ids = set()
        tasks = [t for t in preview if t["id"] in selected_ids]
    else:
        tasks = preview.copy()

    if not hasattr(request.user, "teacher"):
        return HttpResponseForbidden("Генерация доступна только учителям")

    total_time = sum(int(t.get("time_minutes", 10)) for t in tasks)
    if total_time > MAX_TIME:
        return HttpResponse(
            f"Ошибка: суммарное время задач {total_time} мин "
            f"превышает лимит {MAX_TIME} мин.",
            status=400
        )

    templates = get_tasks_list()
    template_map = {t.id: t for t in templates}

    temp_dir = tempfile.mkdtemp()
    tex_path = os.path.join(temp_dir, "document.tex")

    school = getattr(request.user, "school_name", "Не указано")
    today = date.today().strftime("%d.%m.%Y")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\usepackage{geometry, graphicx, amsmath, amssymb, tikz}
\geometry{a4paper, margin=1in}
\begin{document}
""")

        for student_idx in range(1, num_students + 1):
            # 🔹 Шапка
            f.write(r"\begin{center}" + "\n")
            f.write(r"\LARGE \textbf{Контрольная работа} \\[0.3em]" + "\n")
            f.write(f"{r'{\fontsize{20}{16}\selectfont \textbf{Вариант №'}{student_idx}{r'}}\\[0.3em]'}\n")
            f.write(r"\rule{\textwidth}{0.5pt}" + "\n")  # линия под шапкой
            f.write(r"\end{center}" + "\n\n")


            # 🔹 Правые данные
            f.write(r"\begin{flushright}" + "\n")
            f.write(r"{\small" + "\n")
            f.write(f"Учитель: {latex_escape(request.user.get_full_name())}\\\\[0.2em]\n")
            f.write(f"Школа: {latex_escape(school)}\\\\[0.2em]\n")
            f.write(f"Количество учеников: {num_students}\\\\[0.2em]\n")
            f.write(f"Дата: {today}\\\\[0.2em]\n")
            f.write(f"Общее время: {total_time} минут\\\\\n")
            f.write(r"}" + "\n")
            f.write(r"\end{flushright}" + "\n\n")


            # 🔹 Задачи
            for i, t in enumerate(tasks, 1):
                tmpl = template_map.get(t["template_id"])
                if tmpl and hasattr(tmpl, "generate"):
                    task_data = tmpl.generate()  # новый вариант для каждого ученика
                else:
                    task_data = t

                task_text = task_data["task"]
                solution = task_data.get("solution", "")

                f.write(f"\\subsection*{{Задача {i}}}\n")
                f.write(f"\\textbf{{Тема:}} {latex_escape(t['topic'])}\\\\\n")
                f.write(f"\\textbf{{Уровень:}} {t.get('level',1)}\\\\\n")
                f.write(f"\\textbf{{Время:}} {t.get('time_minutes',10)} минут\\\\[6pt]\n")
                f.write(f"\\textbf{{Описание:}} {latex_escape(t.get('description',''))}\\\\[6pt]\n")
                f.write(latex_escape(str(task_text)) + "\n\n")

                if t.get("tikz"):
                    f.write(t["tikz"] + "\n\n")

                if with_solutions and solution:
                    f.write("\\textbf{Решение:}\\\\\n")
                    f.write(latex_escape(str(solution)) + "\n\n")

            f.write(r"\newpage" + "\n")

        f.write(r"\end{document}")

    ok = compile_latex("document.tex", temp_dir)
    pdf_path = os.path.join(temp_dir, "document.pdf")
    if not ok or not os.path.exists(pdf_path):
        log_path = os.path.join(temp_dir, "document.log")
        log_text = ""
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
                log_text = lf.read()
        return HttpResponse(f"Ошибка LaTeX:<pre>{log_text}</pre>")

    return FileResponse(open(pdf_path, "rb"),
                        as_attachment=True,
                        filename="exam.pdf")
