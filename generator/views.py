# generator/views.py
import os
import tempfile
import json
import random
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from tasks.tasks import get_generators
from .utils import latex_escape, LEVEL_TIME, MAX_TIME, compile_latex

# number of preview items to show
PREVIEW_COUNT = 8

def make_preview_list():
    """
    Генерируем PREVIEW_COUNT задач (каждый раз уникальные),
    возвращаем список словарей, пригодных для серриализации в сессию.
    """
    gens = get_generators()
    preview = []
    i = 1
    # выбираем случайные генераторы, вызываем их
    while len(preview) < PREVIEW_COUNT:
        gen = random.choice(gens)
        t = gen()
        # нормализуем поля, убедимся, что значения сериализуемы
        preview.append({
            "id": i,
            "topic": t.get("topic"),
            "description": t.get("description"),
            "task": t.get("task"),
            "solution": t.get("solution"),
            "level": t.get("level"),
            "time_minutes": t.get("time_minutes"),
            "tikz": t.get("tikz"),
        })
        i += 1
    return preview

def index(request):
    """
    Отображаем страницу выбора задач.
    Генерируем превью и сохраняем его в сессии для последующей генерации PDF.
    """
    preview = make_preview_list()
    # сохраняем в сессии JSON-совместимую структуру
    request.session['preview_tasks'] = preview
    request.session.modified = True

    # собираем уникальные темы для фильтра
    all_topics = sorted({t["topic"] for t in preview if t.get("topic")})
    context = {
        "tasks": preview,
        "all_topics": all_topics,
    }
    return render(request, "generator/index.html", context)


@require_http_methods(["POST"])
def generate_pdf(request):
    """
    Получает POST: selected_tasks (может быть несколько),
    параметр with_solutions (checkbox).
    Берёт preview_tasks из сессии и составляет PDF.
    """
    # получаем список выбранных id как строки
    selected = request.POST.getlist("selected_tasks")
    with_solutions = request.POST.get("with_solutions") == "on"

    preview = request.session.get("preview_tasks", [])
    
    # фильтруем выбранные
    if selected:
        selected_ids = set(int(x) for x in selected)
        tasks = [t for t in preview if t["id"] in selected_ids]
    else:
        # если ничего не выбрано — берём первые, пока не уложимся в MAX_TIME
        tasks = preview.copy()

    # Ограничение по времени: выбираем последовательно
    chosen = []
    total_time = 0
    for t in tasks:
        t_time = int(t.get("time_minutes") or LEVEL_TIME.get(t.get("level", 1), 10))
        if total_time + t_time <= MAX_TIME:
            chosen.append(t)
            total_time += t_time

    # Если по какой-то причине ничего не выбрано (например, превью слишком большие) — берем один элемент
    if not chosen and preview:
        chosen = [preview[0]]
        total_time = LEVEL_TIME.get(preview[0].get("level", 1), 10)

    # ==== Формируем LaTeX ====
    temp_dir = tempfile.mkdtemp()
    tex_name = "document.tex"
    tex_path = os.path.join(temp_dir, tex_name)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(r"""\documentclass[12pt]{article}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\usepackage{amsmath,amssymb}
\usepackage{geometry}
\usepackage{tikz}
\usetikzlibrary{calc}
\geometry{a4paper, margin=1in}
\begin{document}
""")
        f.write(f"\\section*{{Контрольная работа}}\n")
        f.write(f"Общее время: {total_time} минут.\\\\[12pt]\n")

        for i, t in enumerate(chosen, 1):
            f.write(f"\\subsection*{{Задача {i}}}\n")
            f.write(f"\\textbf{{Тема:}} {latex_escape(str(t.get('topic','')))}\\\\\n")
            f.write(f"\\textbf{{Уровень:}} {t.get('level')}\\\\\n")
            f.write(f"\\textbf{{Время:}} {t.get('time_minutes')} минут\\\\[6pt]\n")
            f.write(f"\\textbf{{Описание:}} {latex_escape(str(t.get('description','')))}\\\\[6pt]\n")

            # условие — в тз уже есть формулы в $...$, не экранируем $-части
            f.write(t.get("task", "") + "\n\n")

            # TikZ-рисунок, если есть
            if t.get("tikz"):
                f.write(t.get("tikz") + "\n\n")

            if with_solutions and t.get("solution"):
                f.write("\\textbf{Решение:}\\\\\n")
                f.write(latex_escape(str(t.get("solution"))) + "\n\n")

        f.write(r"\end{document}")

    # компиляция
    ok = compile_latex(tex_name, temp_dir)
    pdf_path = os.path.join(temp_dir, "document.pdf")
    if not ok or not os.path.exists(pdf_path):
        # при ошибке покажем лог (xelatex лог)
        log_path = os.path.join(temp_dir, "document.log")
        log_text = ""
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8", errors="ignore") as lf:
                log_text = lf.read()
        return HttpResponse(f"Ошибка компиляции LaTeX. Лог:\n\n<pre>{log_text}</pre>")

    # возвращаем файл
    response = FileResponse(open(pdf_path, "rb"), as_attachment=True, filename="exam.pdf")
    return response
