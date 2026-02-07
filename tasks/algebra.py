from tasks.base import TaskTemplate

ALGEBRA_TASKS = []

ALGEBRA_TASKS.append(
    TaskTemplate(
        id="alg_001",
        topic="Алгебра",
        level=7,
        source="Макарычев №312",
        params={"a": [2, 3, 4], "b": [5, 7, 9]},
        task_template="Решите уравнение: {a}x + {b} = 0",
        solution_template="Переносим {b} вправо: {a}x = -{b}, x = {result}",
        formula=lambda p: -p["b"] / p["a"],
        time_minutes=10
    )
)
