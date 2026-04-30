import random
from .formulas import FORMULAS
from .generators import CUSTOM_GENERATORS


def normalize_number(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def generate_task_instance(task):
    if task.task_type == "custom_generator":
        generator = CUSTOM_GENERATORS.get(task.custom_generator_name)
        if not generator:
            raise ValueError(f"Не найден кастомный генератор: {task.custom_generator_name}")
        return generator(task)

    values = {}

    for key, variants in (task.params or {}).items():
        if not variants:
            raise ValueError(f"Пустой список параметров '{key}' в задаче ID={task.id}")
        values[key] = random.choice(variants)

    if task.task_type == "template_formula":
        if not task.formula:
            raise ValueError(f"У задачи ID={task.id} не выбрана формула")
        formula_func = FORMULAS.get(task.formula.code)
        if not formula_func:
            raise ValueError(f"Формула '{task.formula.code}' не зарегистрирована")
        result = formula_func(values)
        values["result"] = normalize_number(result)

    try:
        task_text = task.task_template.format(**values)
        solution_text = task.solution_template.format(**values) if task.solution_template else ""
        tikz_text = task.tikz_template.format(**values) if task.tikz_template else ""
    except KeyError as e:
        raise ValueError(f"Не хватает параметра {e} в задаче ID={task.id}")

    return {
        "id": task.id,
        "title": task.title,
        "topic": task.topic.name,
        "subtopic": task.subtopic.name if task.subtopic else "",
        "source": task.source,
        "source_number": task.source_number,
        "task": task_text,
        "solution": solution_text,
        "tikz": tikz_text,
        "time_minutes": task.time_minutes,
        "difficulty": task.difficulty,
    }