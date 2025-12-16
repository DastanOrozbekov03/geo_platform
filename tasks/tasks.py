# tasks/tasks.py
import inspect
from tasks import geometry, algebra

# ===== АВТО-ДЕТЕКТОР ФУНКЦИЙ =====

def _collect_functions_from_module(module):
    """
    Находит все функции в переданном модуле,
    исключая служебные (начинающиеся с "_").
    """
    funcs = []
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith("_"):
            funcs.append(obj)
    return funcs


# ===== АВТО-СБОРЩИК ГОТОВЫХ СПИСКОВ =====

def _collect_list_from_module(module, var_name):
    """
    Возвращает список задач из модуля, если такая переменная есть.
    Например: GEOMETRY_TASKS или ALGEBRA_TASKS.
    """
    return getattr(module, var_name, [])


# ===== ГЛАВНАЯ ФУНКЦИЯ =====

def get_tasks_list():
    """
    Собирает ВСЕ задачи:
    • статические списки (GEOMETRY_TASKS, ALGEBRA_TASKS)
    • ВСЕ функции из geometry.py
    • ВСЕ функции из algebra.py
    """
    geometry_static = _collect_list_from_module(geometry, "GEOMETRY_TASKS")
    algebra_static = _collect_list_from_module(algebra, "ALGEBRA_TASKS")

    geometry_funcs = _collect_functions_from_module(geometry)
    algebra_funcs = _collect_functions_from_module(algebra)

    # финальный большой список
    return (
        list(geometry_static)
        + list(algebra_static)
        + list(geometry_funcs)
        + list(algebra_funcs)
    )





