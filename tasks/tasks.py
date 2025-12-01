# tasks/tasks.py
import random
from math import sqrt

# ---------------------
# Генераторы задач
# ---------------------

def algebra_expression():
    """
    Генерирует простую алгебраическую задачу: вычислить значение многочлена при заданном x.
    Решение возвращается в текстовом виде. TikZ не используется.
    """
    a = random.randint(1, 9)
    b = random.randint(0, 9)
    c = random.randint(0, 9)
    x = random.randint(1, 6)
    expr = f"{a}x^2 + {b}x + {c}"
    value = a * x * x + b * x + c

    return {
        "topic": "Алгебра",
        "description": "Подставить значение x и вычислить выражение.",
        "task": rf"Найдите значение выражения ${a}x^2 + {b}x + {c}$ при $x = {x}$.",
        "solution": rf"Подставляем $x={x}$: {a}({x}^2) + {b}({x}) + {c} = {value}.",
        "level": random.choice([1, 1, 2]),
        "time_minutes": 10,
        "tikz": None,
    }


def triangle_angles_task():
    """
    Геометрическая задача с TikZ: треугольник с рандомной высотой.
    Условие — сумма углов. TikZ рисует треугольник.
    """
    # случайная высота для видимого варианта
    h = random.randint(2, 5)
    base = random.randint(4, 6)
    # TikZ coordinates: A(0,0), B(base,0), C(base/2, h)
    tikz = rf"""
\begin{{center}}
\begin{{tikzpicture}}[scale=0.9]
    \coordinate (A) at (0,0);
    \coordinate (B) at ({base},0);
    \coordinate (C) at ({base/2},{h});
    \draw[thick] (A) -- (B) -- (C) -- cycle;
    \node[left] at (A) {{A}};
    \node[right] at (B) {{B}};
    \node[above] at (C) {{C}};
    % расстояния
    \draw[dashed] ({base/2},0) -- ({base/2},{h});
    \node[below] at ({base/2},0) {{h}};
\end{{tikzpicture}}
\end{{center}}
"""
    return {
        "topic": "Геометрия",
        "description": "Свойства треугольника — сумма углов.",
        "task": r"Докажите, что сумма углов треугольника равна $180^\circ$.",
        "solution": r"Проведём через вершину С прямую, параллельную AB, и получим два накрест лежащих угла; их сумма с углом в вершине даёт 180°.",
        "level": random.choice([2, 3]),
        "time_minutes": 15,
        "tikz": tikz,
    }


def right_triangle_area_task():
    """
    Задача на площадь прямоугольного треугольника с TikZ и числами.
    Подставляются случайные катеты.
    """
    a = random.randint(3, 8)
    b = random.randint(2, 7)
    area = 0.5 * a * b
    tikz = rf"""
\begin{{center}}
\begin{{tikzpicture}}[scale=0.8]
    \coordinate (A) at (0,0);
    \coordinate (B) at ({a},0);
    \coordinate (C) at (0,{b});
    \draw[thick] (A) -- (B) -- (C) -- cycle;
    \draw (0.4,0) arc (0:90:0.4);
    \node[below] at ({a/2},0) {{a={a}}};
    \node[left] at (0,{b/2}) {{b={b}}};
\end{{tikzpicture}}
\end{{center}}
"""
    return {
        "topic": "Геометрия",
        "description": "Найдите площадь прямоугольного треугольника.",
        "task": rf"Найдите площадь треугольника с катетами $a={a}$ и $b={b}$.",
        "solution": rf"S = \\frac{{1}}{{2}}ab = \\frac{{1}}{{2}} \\cdot {a} \\cdot {b} = {area}.",
        "level": random.choice([1, 2]),
        "time_minutes": 10,
        "tikz": tikz,
    }


def circle_circumference_task():
    """
    Задача по окружности: найти длину окружности по радиусу.
    """
    r = random.randint(2, 6)
    circumference = round(2 * 3.1416 * r, 2)
    tikz = rf"""
\begin{{center}}
\begin{{tikzpicture}}[scale=0.9]
    \draw (0,0) circle ({r});
    \node at (0,0) {{O}};
    \draw[->] (0,0) -- ({r},0) node[right] {{r}};
\end{{tikzpicture}}
\end{{center}}
"""
    return {
        "topic": "Геометрия",
        "description": "Окружность — длина окружности.",
        "task": rf"Найдите длину окружности радиуса $r={r}$ (используйте $\pi \\approx 3.1416$).",
        "solution": rf"L = 2\pi r \\approx 2 \\cdot 3.1416 \\cdot {r} = {circumference}.",
        "level": 2,
        "time_minutes": 12,
        "tikz": tikz,
    }

# ---------------------
# Реестр генераторов
# ---------------------
def get_generators():
    """
    Возвращает список функций-генераторов.
    Можно добавлять сюда новые функции.
    """
    return [
        algebra_expression,
        triangle_angles_task,
        right_triangle_area_task,
        circle_circumference_task,
        algebra_expression,
        right_triangle_area_task,
    ]
