import random

ALGEBRA_TASKS = [
    {
        "topic": "Алгебра",
        "level": 1,
        "time": 6,
        "description": "Решите линейное уравнение.",
        "generator": lambda: (
            lambda a, b, c: f"Решите уравнение: {a}x + {b} = {c}."
        )(
            random.randint(2, 9),
            random.randint(1, 9),
            random.randint(2, 9) * random.randint(1, 9)
        )
    },
    {
        "topic": "Алгебра",
        "level": 3,
        "time": 12,
        "description": "Решите квадратное уравнение.",
        "generator": lambda: (
            lambda a, b, c: f"Решите квадратное уравнение: {a}x² + {b}x + {c} = 0."
        )(
            random.randint(1, 3),
            random.randint(-10, 10),
            random.randint(-10, 10)
        )
    },
]
