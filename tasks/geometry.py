import random

GEOMETRY_TASKS = [
    {
        "topic": "Геометрия",
        "level": 1,
        "time": 5,
        "description": "Найдите периметр треугольника. Это задача №5",
        "generator": lambda: (
            lambda a, b, c: f"Найдите периметр треугольника со сторонами {a}, {b}, {c}."
        )(*(random.randint(3, 12) for _ in range(3)))
    },
    {
        "topic": "Геометрия",
        "level": 2,
        "time": 10,
        "description": "Найдите площадь прямоугольника. Это задача №6",
        "generator": lambda: (
            lambda w, h: f"Найдите площадь прямоугольника: {w} × {h}."
        )(random.randint(2, 15), random.randint(2, 15))
    },
    {
        "topic": "Геометрия",
        "level": 3,
        "time": 15,
        "description": "Найдите площадь круга.  Это задача №7",
        "generator": lambda: (
            lambda r: f"Найдите площадь круга с радиусом {r}."
        )(random.randint(1, 10))
    }
]


# ============= ДОПОЛНИТЕЛЬНЫЕ ГЕОМЕТРИЧЕСКИЕ ЗАДАЧИ =============

def triangle_angles_task():
    """
    Геометрическая задача: сумма углов треугольника + TikZ рисунок.
    """
    h = random.randint(2, 5)
    base = random.randint(4, 6)

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
    \draw[dashed] ({base/2},0) -- ({base/2},{h});
    \node[below] at ({base/2},0) {{h}};
\end{{tikzpicture}}
\end{{center}}
"""

    return {
        "topic": "Геометрия",
        "description": "Свойства треугольника — сумма углов. Это задача №2",
        "task": r"Докажите, что сумма углов треугольника равна $180^\circ$.",
        "solution": r"Проведите через вершину C прямую, параллельную AB. Накрест лежащие углы дадут сумму $180^\circ$.",
        "level": random.choice([2, 3]),
        "time_minutes": 15,
        "tikz": tikz,
    }


def right_triangle_area_task():
    """
    Площадь прямоугольного треугольника + TikZ.
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
        "description": "Найдите площадь прямоугольного треугольника. Задача №3",
        "task": rf"Найдите площадь треугольника с катетами $a={a}$ и $b={b}$.",
        "solution": rf"S = \frac{{1}}{{2}}ab = \frac{{1}}{{2}} \cdot {a} \cdot {b} = {area}.",
        "level": random.choice([1, 2]),
        "time_minutes": 10,
        "tikz": tikz,
    }


def circle_circumference_task():
    """
    Длина окружности по радиусу.
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
        "description": "Окружность — длина окружности. Это задача №4",
        "task": rf"Найдите длину окружности радиуса $r={r}$ (возьмите $\pi \approx 3.1416$).",
        "solution": rf"L = 2\pi r \approx 2 \cdot 3.1416 \cdot {r} = {circumference}.",
        "level": 2,
        "time_minutes": 10,
        "tikz": tikz,
    }
