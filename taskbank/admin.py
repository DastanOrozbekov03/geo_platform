from django.contrib import admin
from django.utils.safestring import mark_safe

from .forms import TaskAdminForm
from .models import Subject, Topic, SubTopic, Formula, Task


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "subject")
    list_filter = ("subject",)
    search_fields = ("name", "subject__name")


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "topic")
    list_filter = ("topic", "topic__subject")
    search_fields = ("name", "topic__name", "topic__subject__name")


@admin.register(Formula)
class FormulaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "description")
    list_editable = ("is_active",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm

    list_display = (
        "id",
        "title",
        "grade",
        "subject",
        "topic",
        "subtopic",
        "task_type",
        "difficulty",
        "formula",
        "time_minutes",
        "is_active",
    )
    list_filter = (
        "grade",
        "subject",
        "topic",
        "subtopic",
        "task_type",
        "difficulty",
        "is_active",
    )
    search_fields = (
        "title",
        "source",
        "source_number",
        "task_template",
        "solution_template",
    )
    list_editable = ("time_minutes", "is_active")
    autocomplete_fields = ("subject", "topic", "subtopic", "formula")
    save_on_top = True

    readonly_fields = ("created_at", "updated_at", "admin_help_block")

    fieldsets = (
        ("Где находится задача", {
            "fields": (
                "subject",
                "topic",
                "subtopic",
                "grade",
            )
        }),
        ("Паспорт задачи", {
            "fields": (
                "title",
                "source",
                "source_number",
                "difficulty",
                "time_minutes",
                "is_active",
            )
        }),
        ("Тип задачи", {
            "fields": (
                "task_type",
                "admin_help_block",
            )
        }),
        ("Содержимое", {
            "fields": (
                "task_template",
                "solution_template",
            )
        }),
        ("Удобное заполнение параметров", {
            "fields": (
                "numeric_param_names",
                ("number_from", "number_to", "number_step"),
                "use_letter_params",
                "letter_param_names",
                "uppercase_letters",
                "lowercase_letters",
            )
        }),
        ("Продвинутый режим", {
            "classes": ("collapse",),
            "fields": (
                "params",
                "formula",
                "custom_generator_name",
                "tikz_template",
            )
        }),
        ("Служебное", {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    def admin_help_block(self, obj=None):
        return mark_safe(
            """
            <div style="padding:12px 14px; border-radius:10px; background:#f8f9fa; border:1px solid #dee2e6;">
                <strong>Как теперь проще заполнять:</strong>
                <ul style="margin:10px 0 0 18px;">
                    <li>Для чисел можно не писать JSON, а указать имена параметров и диапазон.</li>
                    <li>Для букв можно включить "Заменять буквы" и указать имена переменных.</li>
                    <li>Поле JSON остаётся для сложных случаев и ручного режима.</li>
                    <li>Если JSON пустой, форма попробует собрать параметры автоматически.</li>
                </ul>
            </div>
            """
        )

    admin_help_block.short_description = "Подсказка"

class TaskAdmin(admin.ModelAdmin):
    ...

    class Media:
        js = ("admin/task_param_helper.js",)