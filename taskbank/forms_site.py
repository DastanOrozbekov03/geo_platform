from django import forms
from .models import Subject, Topic, SubTopic, Formula, Task


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Например: Геометрия"
            })
        }


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["subject", "name"]
        widgets = {
            "subject": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Например: Треугольники"
            }),
        }


class SubTopicForm(forms.ModelForm):
    class Meta:
        model = SubTopic
        fields = ["topic", "name"]
        widgets = {
            "topic": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Например: Сумма углов треугольника"
            }),
        }


class FormulaForm(forms.ModelForm):
    class Meta:
        model = Formula
        fields = ["name", "code", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Например: Сумма углов треугольника"
            }),
            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Например: triangle_angle_sum"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Например: result = 180 - a - b"
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class TaskSiteForm(forms.ModelForm):
    numeric_param_names = forms.CharField(
        label="Числовые параметры",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Например: a, b, h"
        })
    )

    number_from = forms.IntegerField(
        label="От",
        required=False,
        initial=10,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    number_to = forms.IntegerField(
        label="До",
        required=False,
        initial=80,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    number_step = forms.IntegerField(
        label="Шаг",
        required=False,
        initial=5,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    use_letter_params = forms.BooleanField(
        label="Заменять буквы",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    letter_param_names = forms.CharField(
        label="Буквенные параметры",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Например: A, B, C"
        })
    )

    class Meta:
        model = Task
        fields = [
            "subject",
            "topic",
            "subtopic",
            "grade",
            "title",
            "difficulty",
            "task_template",
            "solution_template",
            "formula",
            "time_minutes",
            "is_active",
            "tikz_template",
        ]

        widgets = {
            "subject": forms.Select(attrs={"class": "form-select"}),
            "topic": forms.Select(attrs={"class": "form-select"}),
            "subtopic": forms.Select(attrs={"class": "form-select"}),
            "grade": forms.NumberInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Например: Сумма углов треугольника"
            }),
            "difficulty": forms.Select(attrs={"class": "form-select"}),
            "task_template": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "В треугольнике {A}{B}{C} угол {A} = {a}°, угол {B} = {b}°. Найдите угол {C}."
            }),
            "solution_template": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Угол {C} = 180° - {a}° - {b}° = {result}°."
            }),
            "tikz_template": forms.Textarea(attrs={
                "class": "form-control font-monospace",
                "rows": 7,
                "placeholder": r"\begin{tikzpicture} ... \end{tikzpicture}"
            }),
            "formula": forms.Select(attrs={"class": "form-select"}),
            "time_minutes": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def _parse_csv(self, value):
        if not value:
            return []
        return [x.strip() for x in value.split(",") if x.strip()]

    def clean(self):
        cleaned_data = super().clean()

        number_from = cleaned_data.get("number_from")
        number_to = cleaned_data.get("number_to")
        number_step = cleaned_data.get("number_step") or 1

        if number_step <= 0:
            self.add_error("number_step", "Шаг должен быть больше 0.")

        if number_from is not None and number_to is not None:
            if number_from > number_to:
                self.add_error("number_from", "Поле 'От' не может быть больше поля 'До'.")

        return cleaned_data

    def save(self, commit=True):
        task = super().save(commit=False)

        task.task_type = "template_formula"
        task.custom_generator_name = ""

        params = {}

        numeric_names = self._parse_csv(self.cleaned_data.get("numeric_param_names"))
        number_from = self.cleaned_data.get("number_from")
        number_to = self.cleaned_data.get("number_to")
        number_step = self.cleaned_data.get("number_step") or 1

        if numeric_names and number_from is not None and number_to is not None:
            values = list(range(number_from, number_to + 1, number_step))
            for name in numeric_names:
                params[name] = values

        if self.cleaned_data.get("use_letter_params"):
            letter_names = self._parse_csv(self.cleaned_data.get("letter_param_names"))
            letters = ["A", "B", "C", "D", "M", "N", "K", "L", "P", "Q", "R", "S", "T"]

            for name in letter_names:
                params[name] = letters

        task.params = params

        if commit:
            task.save()

        return task