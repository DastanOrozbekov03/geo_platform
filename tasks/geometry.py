import random

GEOMETRY_TASKS = [
    {
        "topic": "Геометрия",
        "level": 1,
        "time": 5,
        "description": "Найдите периметр треугольника.",
        "generator": lambda: (
            lambda a, b, c: f"Найдите периметр треугольника со сторонами {a}, {b}, {c}."
        )(*(random.randint(3, 12) for _ in range(3)))
    },
    {
        "topic": "Геометрия",
        "level": 2,
        "time": 7,
        "description": "Найдите площадь прямоугольника.",
        "generator": lambda: (
            lambda w, h: f"Найдите площадь прямоугольника: {w} × {h}."
        )(random.randint(2, 15), random.randint(2, 15))
    },
]
