import random


def generate_isosceles_triangle_angles(task):
    a = random.choice([20, 30, 40, 50, 60, 70])
    result = (180 - a) / 2

    return {
        "id": task.id,
        "title": task.title,
        "topic": task.topic.name,
        "subtopic": task.subtopic.name if task.subtopic else "",
        "source": task.source,
        "source_number": task.source_number,
        "task": f"В равнобедренном треугольнике угол при вершине равен {a}°. Найдите углы при основании.",
        "solution": f"Сумма двух углов при основании: 180° - {a}° = {180 - a}°. Каждый угол равен {result}°.",
        "tikz": "",
        "time_minutes": task.time_minutes,
        "difficulty": task.difficulty,
    }


CUSTOM_GENERATORS = {
    "isosceles_triangle_angles": generate_isosceles_triangle_angles,
}