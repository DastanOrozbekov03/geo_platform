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
    autocomplete_fields = ("subject",)


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "topic")
    list_filter = ("topic", "topic__subject")
    search_fields = ("name", "topic__name", "topic__subject__name")
    autocomplete_fields = ("topic",)


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
        "difficulty",
        "formula",
        "is_active",
    )

    search_fields = (
        "title",
        "task_template",
        "solution_template",
    )

    list_editable = ("time_minutes", "is_active")
    autocomplete_fields = ("subject", "topic", "subtopic", "formula")
    save_on_top = True

    readonly_fields = (
        "admin_help_block",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("1. Основная информация", {
            "fields": (
                "admin_help_block",
                "subject",
                "topic",
                "subtopic",
                "grade",
                "title",
                "difficulty",
                "time_minutes",
                "is_active",
            )
        }),

        ("2. Текст задачи", {
            "fields": (
                "task_template",
                "solution_template",
            )
        }),

        ("3. Параметры задачи", {
            "fields": (
                "numeric_param_names",
                ("number_from", "number_to", "number_step"),
                "use_letter_params",
                "letter_param_names",
                "uppercase_letters",
                "lowercase_letters",
            )
        }),

        ("4. Формула", {
            "fields": (
                "formula",
            )
        }),

        ("Служебная информация", {
            "classes": ("collapse",),
            "fields": (
                "params",
                "task_type",
                "source",
                "source_number",
                "custom_generator_name",
                "tikz_template",
                "created_at",
                "updated_at",
            )
        }),
    )

    def admin_help_block(self, obj=None):
        return mark_safe("""
        <div style="
            padding:14px 16px;
            border-radius:12px;
            background:#eef6ff;
            border:1px solid #b6dcff;
            margin-bottom:10px;
        ">
            <strong style="font-size:15px;">Обычный режим добавления задачи</strong>
            <ul style="margin:10px 0 0 20px;">
                <li>В тексте задачи используй параметры: <code>{a}</code>, <code>{b}</code>, <code>{A}</code>, <code>{B}</code>, <code>{result}</code>.</li>
                <li>Числовые параметры указывай через запятую: <code>a, b, h</code>.</li>
                <li>Для букв включи “Заменять буквы” и укажи: <code>A, B, C</code>.</li>
                <li>JSON заполнять не надо — система соберёт его автоматически.</li>
                <li>Тип задачи автоматически ставится как “Шаблон + формула”.</li>
            </ul>
        </div>
        """)

    admin_help_block.short_description = "Подсказка"

    class Media:
        js = ("admin/task_param_helper.js",)