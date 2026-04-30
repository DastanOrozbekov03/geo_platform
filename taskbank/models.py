from django.db import models


class Subject(models.Model):
    name = models.CharField("Предмет", max_length=100, unique=True)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Topic(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name="Предмет"
    )
    name = models.CharField("Тема", max_length=200)

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        ordering = ["subject__name", "name"]
        unique_together = ("subject", "name")

    def __str__(self):
        return f"{self.subject} → {self.name}"


class SubTopic(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="subtopics",
        verbose_name="Тема"
    )
    name = models.CharField("Подтема", max_length=200)

    class Meta:
        verbose_name = "Подтема"
        verbose_name_plural = "Подтемы"
        ordering = ["topic__name", "name"]
        unique_together = ("topic", "name")

    def __str__(self):
        return f"{self.topic} → {self.name}"


class Formula(models.Model):
    code = models.CharField("Код формулы", max_length=100, unique=True)
    name = models.CharField("Название формулы", max_length=255)
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Формула"
        verbose_name_plural = "Формулы"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Task(models.Model):
    DIFFICULTY_CHOICES = (
        (1, "Лёгкая"),
        (2, "Средняя"),
        (3, "Сложная"),
    )

    TASK_TYPE_CHOICES = (
        ("theory", "Теория / определение"),
        ("template_only", "Шаблон без формулы"),
        ("template_formula", "Шаблон + формула"),
        ("proof", "Доказательство"),
        ("geometry_tikz", "Геометрия с чертежом"),
        ("custom_generator", "Кастомный генератор"),
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Предмет"
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Тема"
    )
    subtopic = models.ForeignKey(
        SubTopic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Подтема"
    )

    grade = models.PositiveSmallIntegerField("Класс", default=7)
    difficulty = models.PositiveSmallIntegerField(
        "Сложность",
        choices=DIFFICULTY_CHOICES,
        default=1
    )

    title = models.CharField("Название задачи", max_length=255)
    source = models.CharField("Источник", max_length=255, blank=True)
    source_number = models.CharField("Номер в источнике", max_length=50, blank=True)

    task_type = models.CharField(
        "Тип задачи",
        max_length=30,
        choices=TASK_TYPE_CHOICES,
        default="template_formula"
    )

    task_template = models.TextField("Текст задачи")
    solution_template = models.TextField("Решение / ответ", blank=True)

    params = models.JSONField(
        "Параметры (JSON)",
        default=dict,
        blank=True,
        help_text='Например: {"a": [4,5,6], "h": [3,4,5]}'
    )

    formula = models.ForeignKey(
        Formula,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Формула"
    )

    custom_generator_name = models.CharField(
        "Имя кастомного генератора",
        max_length=100,
        blank=True
    )

    tikz_template = models.TextField("TikZ шаблон", blank=True)

    time_minutes = models.PositiveSmallIntegerField("Время (мин.)", default=10)
    is_active = models.BooleanField("Активна", default=True)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["grade", "subject__name", "topic__name", "title"]

    def __str__(self):
        source_part = f" {self.source_number}" if self.source_number else ""
        return f"{self.title}{source_part}".strip()