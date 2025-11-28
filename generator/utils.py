from tasks.tasks import get_tasks_list
import tempfile
import subprocess
import os

LEVEL_TIME = {1: 10, 2: 15, 3: 20}
MAX_TIME = 45


def latex_escape(text: str) -> str:
    """
    Экранируем спецсимволы LaTeX, чтобы ничего не упало.
    """
    replace_map = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    for k, v in replace_map.items():
        text = text.replace(k, v)
    return text


def generate_pdf_from_tasks(selected_ids, with_solutions=False):
    tasks = get_tasks_list()

    # фильтрация по выбранным задачам
    if selected_ids:
        tasks = [t for t in tasks if t["id"] in selected_ids]

    # если ничего не выбрали — берём все
    if not tasks:
        tasks = get_tasks_list()

    # ==== Ограничение по времени ====
    chosen = []
    total_time = 0

    for t in tasks:
        t_time = LEVEL_TIME.get(t["level"], 10)
        if total_time + t_time <= MAX_TIME:
            chosen.append(t)
            total_time += t_time

    tasks = chosen

    # ==== создаём временный каталог ====
    temp_dir = tempfile.mkdtemp()
    tex_path = os.path.join(temp_dir, "document.tex")

    # ==== пишем LaTeX ====
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(r"""
\documentclass[12pt]{article}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\usepackage{amsmath}
\usepackage{geometry}
\usepackage{enumitem}
\geometry{a4paper, margin=1in}
\begin{document}
""")

        # заголовок
        f.write(f"\\section*{{Контрольная работа}}\n")
        f.write(f"Общее время: {total_time} минут.\\\\[12pt]\n")

        # задачи
        for i, t in enumerate(tasks, 1):
            f.write(f"\\subsection*{{Задача {i}}}\n")
            f.write(f"\\textbf{{Тема:}} {latex_escape(t['topic'])}\\\\\n")
            f.write(f"\\textbf{{Уровень:}} {t['level']}\\\\\n")
            f.write(f"\\textbf{{Время:}} {LEVEL_TIME[t['level']]} минут\\\\[6pt]\n")
            f.write(f"\\textbf{{Описание:}} {latex_escape(t['description'])}\\\\[6pt]\n")

            # Условие — не экранируем $...$ внутри math
            f.write(t['task'] + "\n\n")

            # Решение — только если выбрано
            if with_solutions and t.get("solution"):
                f.write("\\textbf{Решение:}\\\\\n")
                f.write(latex_escape(t['solution']) + "\n\n")

        f.write(r"\end{document}")

    # ==== компиляция LaTeX → PDF ====
    subprocess.run(
        ["xelatex", "-interaction=nonstopmode", "document.tex"],
        cwd=temp_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    pdf_path = os.path.join(temp_dir, "document.pdf")

    return pdf_path
