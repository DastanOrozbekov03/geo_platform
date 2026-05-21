import random
from .formulas import FORMULAS
from .generators import CUSTOM_GENERATORS


def normalize_number(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value

def get_text_for_drawing_detection(task):
    parts = [
        task.title or "",
        task.topic.name if task.topic else "",
        task.subtopic.name if task.subtopic else "",
        task.task_template or "",
    ]
    return " ".join(parts).lower()


def v(values, key, default):
    return values.get(key, default)


def generate_auto_tikz(task, values):
    text = get_text_for_drawing_detection(task)

    if "треуголь" in text:
        A = v(values, "A", "A")
        B = v(values, "B", "B")
        C = v(values, "C", "C")

        return rf"""
\begin{{center}}
\begin{{tikzpicture}}[scale=0.9]
\coordinate ({A}) at (0,0);
\coordinate ({B}) at (5,0);
\coordinate ({C}) at (2,3);

\draw[thick] ({A}) -- ({B}) -- ({C}) -- cycle;

\node[left] at ({A}) {{$ {A} $}};
\node[right] at ({B}) {{$ {B} $}};
\node[above] at ({C}) {{$ {C} $}};
\end{{tikzpicture}}
\end{{center}}
"""

    if "отрез" in text:
        A = v(values, "A", "A")
        B = v(values, "B", "B")
        length = v(values, "a", "")

        length_label = rf"\node[below] at (2.5,0) {{$ {length} $}};" if length else ""

        return rf"""
\begin{{center}}
\begin{{tikzpicture}}[scale=1]
\coordinate ({A}) at (0,0);
\coordinate ({B}) at (5,0);

\draw[thick] ({A}) -- ({B});

\node[left] at ({A}) {{$ {A} $}};
\node[right] at ({B}) {{$ {B} $}};
{length_label}
\end{{tikzpicture}}
\end{{center}}
"""

    if "прямоуголь" in text:
        A = v(values, "A", "A")
        B = v(values, "B", "B")
        C = v(values, "C", "C")
        D = v(values, "D", "D")
        a = v(values, "a", "")
        b = v(values, "b", "")

        a_label = rf"\node[below] at (2.5,0) {{$ {a} $}};" if a else ""
        b_label = rf"\node[right] at (5,1.5) {{$ {b} $}};" if b else ""

        return rf"""
\begin{{center}}
\begin{{tikzpicture}}[scale=0.9]
\coordinate ({A}) at (0,0);
\coordinate ({B}) at (5,0);
\coordinate ({C}) at (5,3);
\coordinate ({D}) at (0,3);

\draw[thick] ({A}) -- ({B}) -- ({C}) -- ({D}) -- cycle;

\node[left] at ({A}) {{$ {A} $}};
\node[right] at ({B}) {{$ {B} $}};
\node[right] at ({C}) {{$ {C} $}};
\node[left] at ({D}) {{$ {D} $}};

{a_label}
{b_label}
\end{{tikzpicture}}
\end{{center}}
"""

    return ""

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

        if task.tikz_template:
            tikz_text = task.tikz_template.format(**values)
        else:
            tikz_text = generate_auto_tikz(task, values)

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

