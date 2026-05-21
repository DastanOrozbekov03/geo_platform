from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Subject, Topic, SubTopic, Formula, Task
from .forms_site import (
    SubjectForm,
    TopicForm,
    SubTopicForm,
    FormulaForm,
    TaskSiteForm,
)


def admin_only_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        messages.error(request, "Доступ разрешён только администратору.")
        return redirect("home")

    return wrapper


@admin_only_required
def taskbank_dashboard(request):
    return render(request, "taskbank/dashboard.html", {
        "subjects": Subject.objects.all(),
        "topics": Topic.objects.select_related("subject").all(),
        "subtopics": SubTopic.objects.select_related("topic", "topic__subject").all(),
        "formulas": Formula.objects.all(),
        "tasks": Task.objects.select_related(
            "subject", "topic", "subtopic", "formula"
        ).order_by("-id"),
    })


def crud_create(request, form_class, template, success_message):
    form = form_class(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect("taskbank_dashboard")

    return render(request, template, {
        "form": form,
        "back_url": "taskbank_dashboard",
    })


def crud_update(request, model_class, form_class, pk, template, success_message):
    obj = get_object_or_404(model_class, pk=pk)
    form = form_class(request.POST or None, instance=obj)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect("taskbank_dashboard")

    return render(request, template, {
        "form": form,
        "object": obj,
        "back_url": "taskbank_dashboard",
    })


def crud_delete(request, model_class, pk, title, success_message):
    obj = get_object_or_404(model_class, pk=pk)

    if request.method == "POST":
        obj.delete()
        messages.success(request, success_message)
        return redirect("taskbank_dashboard")

    return render(request, "taskbank/confirm_delete.html", {
        "object": obj,
        "title": title,
        "back_url": "taskbank_dashboard",
    })


@admin_only_required
def subject_create(request):
    return crud_create(request, SubjectForm, "taskbank/simple_form.html", "Предмет добавлен.")


@admin_only_required
def subject_update(request, pk):
    return crud_update(request, Subject, SubjectForm, pk, "taskbank/simple_form.html", "Предмет изменён.")


@admin_only_required
def subject_delete(request, pk):
    return crud_delete(request, Subject, pk, "Удалить предмет", "Предмет удалён.")


@admin_only_required
def topic_create(request):
    return crud_create(request, TopicForm, "taskbank/simple_form.html", "Тема добавлена.")


@admin_only_required
def topic_update(request, pk):
    return crud_update(request, Topic, TopicForm, pk, "taskbank/simple_form.html", "Тема изменена.")


@admin_only_required
def topic_delete(request, pk):
    return crud_delete(request, Topic, pk, "Удалить тему", "Тема удалена.")


@admin_only_required
def subtopic_create(request):
    return crud_create(request, SubTopicForm, "taskbank/simple_form.html", "Подтема добавлена.")


@admin_only_required
def subtopic_update(request, pk):
    return crud_update(request, SubTopic, SubTopicForm, pk, "taskbank/simple_form.html", "Подтема изменена.")


@admin_only_required
def subtopic_delete(request, pk):
    return crud_delete(request, SubTopic, pk, "Удалить подтему", "Подтема удалена.")


@admin_only_required
def formula_create(request):
    return crud_create(request, FormulaForm, "taskbank/simple_form.html", "Формула добавлена.")


@admin_only_required
def formula_update(request, pk):
    return crud_update(request, Formula, FormulaForm, pk, "taskbank/simple_form.html", "Формула изменена.")


@admin_only_required
def formula_delete(request, pk):
    return crud_delete(request, Formula, pk, "Удалить формулу", "Формула удалена.")


@admin_only_required
def task_create(request):
    return crud_create(request, TaskSiteForm, "taskbank/task_form.html", "Задача добавлена.")


@admin_only_required
def task_update(request, pk):
    return crud_update(request, Task, TaskSiteForm, pk, "taskbank/task_form.html", "Задача изменена.")


@admin_only_required
def task_delete(request, pk):
    return crud_delete(request, Task, pk, "Удалить задачу", "Задача удалена.")