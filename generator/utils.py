from tasks.tasks import get_tasks_list
import tempfile
import subprocess
import os
import shutil

def generate_pdf_from_tasks():
    tasks = get_tasks_list()

    temp_dir = tempfile.mkdtemp()
    tex_path = os.path.join(temp_dir, "document.tex")

    # ПРЕАМБУЛА: явно указываем шрифт с поддержкой кириллицы
    preamble = r"""
\documentclass[12pt]{article}
\usepackage{fontspec}
% На Windows обычно есть Times New Roman; если нет — попробуй "DejaVu Serif" или "Liberation Serif"
\setmainfont{Times New Roman}[Script=Cyrillic]
\usepackage{polyglossia}
\setmainlanguage{russian}

\usepackage{amsmath}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\parindent=0pt
\parskip=6pt
\begin{document}
"""

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(preamble)
        for i, t in enumerate(tasks, 1):
            f.write(f"\\section*{{Задача {i}}}\n")
            f.write(f"\\textbf{{Тема:}} {t['topic']}\\\\\n")
            f.write(f"\\textbf{{Описание:}} {t['description']}\\\\[6pt]\n")
            f.write(t['task'] + "\n\n")
        f.write(r"\end{document}")

    # Компиляция через xelatex (два прохода для безопасности)
    cmd = ["xelatex", "-interaction=nonstopmode", "document.tex"]
    # выполняем без text=True — чтобы не было проблем с кодировкой в Windows
    result1 = subprocess.run(cmd, cwd=temp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result2 = subprocess.run(cmd, cwd=temp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    pdf_path = os.path.join(temp_dir, "document.pdf")

    if not os.path.exists(pdf_path):
        # печатаем логи (без падения на декодировании)
        out1 = result1.stdout.decode("utf-8", errors="ignore")
        err1 = result1.stderr.decode("utf-8", errors="ignore")
        out2 = result2.stdout.decode("utf-8", errors="ignore")
        err2 = result2.stderr.decode("utf-8", errors="ignore")
        print("=== XELATEX RUN 1 STDOUT ===\n", out1)
        print("=== XELATEX RUN 1 STDERR ===\n", err1)
        print("=== XELATEX RUN 2 STDOUT ===\n", out2)
        print("=== XELATEX RUN 2 STDERR ===\n", err2)
        # оставим временную папку для анализа, если нужно
        raise FileNotFoundError("PDF не создан. Смотри логи XeLaTeX выше.")

    # опционально: удалить вспомогательные файлы, оставив PDF
    for ext in (".aux", ".log", ".out", ".toc"):
        try:
            os.remove(os.path.join(temp_dir, "document" + ext))
        except OSError:
            pass

    # Возвращаем путь к PDF (файл в temp_dir — Django откроет его)
    return pdf_path
