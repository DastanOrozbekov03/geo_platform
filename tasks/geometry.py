from tasks.base import TaskTemplate

GEOMETRY_TASKS = []

# Пример задачи
GEOMETRY_TASKS.append(
    TaskTemplate(
        id="geo_001",
        topic="Геометрия",
        level=7,
        source="Атанасян №234",
        params={"a": [4, 5, 6], "h": [5, 6, 7]},
        task_template="Найдите площадь треугольника с основанием {a} см и высотой {h} см.",
        solution_template="Площадь: S = 1/2 * {a} * {h} = {result}",
        formula=lambda p: p["a"] * p["h"] / 2,
        time_minutes=10
    )
)

GEOMETRY_TASKS.append(
    TaskTemplate(
        id="geo_002",
        topic="Геометрия",
        level=7,
        source="Атанасян №545",
        params={"a": [4, 5, 6]},
        task_template="Найдите площадь квадрата, если его сторона {a} см.",
        solution_template="Площадь: S = {a} * {a} = {result}",
        formula=lambda s: s["a"] ** 2,
        time_minutes=15
    )
)

GEOMETRY_TASKS.append(
    TaskTemplate(
        id="geo_003",
        topic="Геометрия",
        level=7,
        source="Атанасян №546",
        params={"a": [4, 5, 6]},
        task_template="Найдите площадь квадрата, если его сторона {a} см.",
        solution_template="Площадь: S = {a} * {a} = {result}",
        formula=lambda s: s["a"] ** 2,
        time_minutes=15
    )
)