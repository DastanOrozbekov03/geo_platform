import random

# ------------------------------
# ГОТОВЫЕ АЛГЕБРАИЧЕСКИЕ ЗАДАЧИ
# ------------------------------

ALGEBRA_TASKS = [
    {
        "topic": "Алгебра",
        "level": 1,
        "time_minutes": 6,
        "description": "Решите линейное уравнение. Это задача №7",
        "generator": lambda: (
            lambda a, b, c: {
                "topic": "Алгебра",
                "description": "Решите линейное уравнение. Это задача №7",
                "task": f"Решите уравнение: ${a}x + {b} = {c}.$",
                "solution": f"{a}x + {b} = {c} → {a}x = {c - b} → x = {(c - b) / a}",
                "level": 1,
                "time_minutes": 6,
                "tikz": None,
            }
        )(
            random.randint(2, 9),
            random.randint(1, 9),
            random.randint(2, 9) * random.randint(1, 9)
        )
    },

    {
        "topic": "Алгебра",
        "level": 3,
        "time_minutes": 15,
        "description": "Решите квадратное уравнение. Это задача №8",
        "generator": lambda: (
            lambda a, b, c: {
                "topic": "Алгебра",
                "description": "Решите квадратное уравнение. Это задача №8",
                "task": f"Решите квадратное уравнение: ${a}x^2 + {b}x + {c} = 0.$",
                "solution": rf"Используем формулу дискриминанта: D = b^2 - 4ac",
                "level": 3,
                "time_minutes": 15,
                "tikz": None,
            }
        )(
            random.randint(1, 3),
            random.randint(-10, 10),
            random.randint(-10, 10)
        )
    },
]

# ------------------------------
# ДОПОЛНИТЕЛЬНАЯ ЗАДАЧА
# ------------------------------

def algebra_expression():
    """
    Задача №1: подставить x в многочлен и вычислить значение.
    Возвращает корректный словарь задачи.
    """
    a = random.randint(1, 9)
    b = random.randint(0, 9)
    c = random.randint(0, 9)
    x = random.randint(1, 6)
    value = a * x * x + b * x + c

    return {
        "topic": "Алгебра",
        "description": "Подставить значение x и вычислить выражение. Это задача №1",
        "task": rf"Найдите значение выражения ${a}x^2 + {b}x + {c}$ при $x = {x}$.",
        "solution": rf"Подставляем $x={x}$: {a}({x}^2) + {b}({x}) + {c} = {value}.",
        "level": random.choice([1, 1, 2]),
        "time_minutes": 10,
        "tikz": None,
    }
