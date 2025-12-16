# generator/views.py
import os
import tempfile
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from tasks.tasks import get_tasks_list
from .utils import latex_escape, LEVEL_TIME, MAX_TIME, compile_latex


def make_preview_list():
    """
    Генерирует список задач для превью.
    Каждой задаче присваивается уникальный ID.
    """
    preview = []
    uid = 1

    for t in get_tasks_list():

        # === ФОРМАТ 1: t — функция ===
        if callable(t):
            data = t() or {}

            text_value = ""
            if "task" in data:
                text_value = data["task"]
            elif "generator" in data:
                text_value = data["generator"]()
            else:
                text_value = ""

            preview.append({
                "id": uid,
                "topic": data.get("topic", "Без темы"),
                "text": text_value,
                "task": text_value,
                "tikz": data.get("tikz", ""),
                "solution": data.get("solution", ""),
                "description": data.get("description", ""),
                "level": data.get("level", 1),
                "time_minutes": data.get("time_minutes")
                                 or LEVEL_TIME.get(data.get("level", 1), 10),
            })
            uid += 1
            continue

        # === ФОРМАТ 2: t — dict ===
        if isinstance(t, dict):
            if "generator" in t:
                txt = t["generator"]()
            else:
                txt = t.get("task", "")

            preview.append({
                "id": uid,
                "topic": t.get("topic", "Без темы"),
                "text": txt,
                "task": txt,
                "tikz": t.get("tikz", ""),
                "solution": t.get("solution", ""),
                "description": t.get("description", ""),
                "level": t.get("level", 1),
                "time_minutes": t.get("time_minutes")
                                 or LEVEL_TIME.get(t.get("level", 1), 10),
            })

            uid += 1

    return preview


def index(request):
    """
    Страница выбора задач.
    """
    preview = make_preview_list()

    request.session["preview_tasks"] = preview
    request.session.modified = True

    all_topics = sorted({t["topic"] for t in preview})

    return render(request, "generator/index.html", {
        "tasks": preview,
        "all_topics": all_topics,
    })


@require_http_methods(["POST"])
def generate_pdf(request):
    """
    Генерация PDF.
    """
    selected = request.POST.getlist("selected_tasks")
    with_solutions = request.POST.get("with_solutions") == "on"

    preview = request.session.get("preview_tasks", [])

    # --- фильтруем по выбранным id ---
    if selected:
        try:
            selected_ids = {int(x) for x in selected}
        except:
            selected_ids = set()

        tasks = [t for t in preview if t["id"] in selected_ids]
    else:
        tasks = preview.copy()

    # --- проверяем время (жесткое ограничение) ---
    total_time = sum(int(t.get("time_minutes", 10)) for t in tasks)

    if total_time > MAX_TIME:
        return HttpResponse(
            f"Ошибка: суммарное время задач {total_time} мин "
            f"превышает лимит {MAX_TIME} мин.",
            status=400
        )

    chosen = tasks

    # ============ Генерация LaTeX ===============
    temp_dir = tempfile.mkdtemp()
    tex_path = os.path.join(temp_dir, "document.tex")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\usepackage{amsmath,amssymb}
\usepackage{geometry}
\usepackage{tikz}
\geometry{a4paper, margin=1in}
\begin{document}
""")

        f.write("\\section*{Контрольная работа}\n")
        f.write(f"Общее время: {total_time} минут.\\\\[12pt]\n")

        for i, t in enumerate(chosen, 1):
            f.write(f"\\subsection*{{Задача {i}}}\n")
            f.write(f"\\textbf{{Тема:}} {latex_escape(t['topic'])}\\\\\n")
            f.write(f"\\textbf{{Уровень:}} {t['level']}\\\\\n")
            f.write(f"\\textbf{{Время:}} {t['time_minutes']} минут\\\\[6pt]\n")

            f.write(f"\\textbf{{Описание:}} {latex_escape(t.get('description',''))}\\\\[6pt]\n")

            # --- сама задача ---
            task_text = t.get("task", "")
            if isinstance(task_text, dict):
                # защищаем от ошибок типа "dict + str"
                task_text = str(task_text)

            f.write(latex_escape(str(task_text)) + "\n\n")

            # TikZ
            if t.get("tikz"):
                f.write(t["tikz"] + "\n\n")

            # Решение
            if with_solutions and t.get("solution"):
                f.write("\\textbf{Решение:}\\\\\n")
                f.write(latex_escape(str(t["solution"])) + "\n\n")

        f.write(r"\end{document}")

    # ==== Компиляция ====
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
