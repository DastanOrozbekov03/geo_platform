import subprocess
from typing import Tuple

LEVEL_TIME = {
    1: 10,
    2: 15,
    3: 20,
}

MAX_TIME = 45


def latex_escape(text: str) -> str:
    """
    Экранирует специальные символы LaTeX.
    """
    if not text:
        return ""

    text = str(text)

    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    return text


def compile_latex(tex_filename: str, cwd: str) -> Tuple[bool, str]:
    """
    Компилирует LaTeX-файл через xelatex.
    Возвращает:
        (True, stdout/stderr) при успехе
        (False, текст ошибки) при ошибке
    """
    try:
        output_log = ""

        for _ in range(2):
            result = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_filename],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="ignore",
                check=True,
            )
            output_log = (result.stdout or "") + "\n" + (result.stderr or "")

        return True, output_log

    except FileNotFoundError:
        return False, "Команда 'xelatex' не найдена. Убедись, что XeLaTeX установлен и доступен в PATH."

    except subprocess.CalledProcessError as e:
        error_log = (e.stdout or "") + "\n" + (e.stderr or "")
        return False, error_log.strip()