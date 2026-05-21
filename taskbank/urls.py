from django.urls import path
from . import views

urlpatterns = [
    path("", views.taskbank_dashboard, name="taskbank_dashboard"),

    path("subjects/add/", views.subject_create, name="subject_create"),
    path("subjects/<int:pk>/edit/", views.subject_update, name="subject_update"),
    path("subjects/<int:pk>/delete/", views.subject_delete, name="subject_delete"),

    path("topics/add/", views.topic_create, name="topic_create"),
    path("topics/<int:pk>/edit/", views.topic_update, name="topic_update"),
    path("topics/<int:pk>/delete/", views.topic_delete, name="topic_delete"),

    path("subtopics/add/", views.subtopic_create, name="subtopic_create"),
    path("subtopics/<int:pk>/edit/", views.subtopic_update, name="subtopic_update"),
    path("subtopics/<int:pk>/delete/", views.subtopic_delete, name="subtopic_delete"),

    path("formulas/add/", views.formula_create, name="formula_create"),
    path("formulas/<int:pk>/edit/", views.formula_update, name="formula_update"),
    path("formulas/<int:pk>/delete/", views.formula_delete, name="formula_delete"),

    path("tasks/add/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/edit/", views.task_update, name="task_update"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
]