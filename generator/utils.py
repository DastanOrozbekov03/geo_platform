# utils.py
import subprocess
import os

LEVEL_TIME = {1: 10, 2: 15, 3: 20}
MAX_TIME = 45

def latex_escape(text: str) -> str:
    """Экранирует спецсимволы LaTeX в произвольном тексте."""
    replace_map = {
        "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    for k, v in replace_map.items():
        text = text.replace(k, v)
    return text

def compile_latex(tex_filename: str, cwd: str) -> bool:
    """
    Компилирует tex-файл (xelatex) в cwd.
    Возвращает True при успехе.
    """
    try:
        # Запустим xelatex два раза для корректных ссылок/шрифтов
        subprocess.run(["xelatex", "-interaction=nonstopmode", tex_filename], cwd=cwd, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["xelatex", "-interaction=nonstopmode", tex_filename], cwd=cwd, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
