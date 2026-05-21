import json

from django import forms
from .models import Task


class TaskAdminForm(forms.ModelForm):
    params = forms.CharField(
        label="Параметры JSON",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 5,
            "style": "font-family: Consolas, monospace;",
        }),
        help_text="Служебное поле. Обычно заполнять не нужно.",
    )

    numeric_param_names = forms.CharField(
        label="Числовые параметры",
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Например: a, b, h"
        }),
        help_text="Имена числовых параметров через запятую."
    )

    number_from = forms.IntegerField(
        label="От",
        required=False,
        initial=10,
    )

    number_to = forms.IntegerField(
        label="До",
        required=False,
        initial=80,
    )

    number_step = forms.IntegerField(
        label="Шаг",
        required=False,
        initial=5,
    )

    use_letter_params = forms.BooleanField(
        label="Заменять буквы",
        required=False,
        initial=True,
    )

    letter_param_names = forms.CharField(
        label="Буквенные параметры",
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Например: A, B, C"
        }),
        help_text="Имена буквенных параметров через запятую."
    )

    uppercase_letters = forms.CharField(
        label="Большие буквы",
        required=False,
        initial="A,B,C,D,M,N,K,L,P,Q,R,S,T",
    )

    lowercase_letters = forms.CharField(
        label="Маленькие буквы",
        required=False,
        initial="a,b,c,d,m,n,k,l,p,q,r,s,t",
    )

    class Meta:
        model = Task
        fields = "__all__"

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Например: Сумма углов треугольника"
            }),
            "task_template": forms.Textarea(attrs={
                "rows": 7,
                "placeholder": (
                    "Например: В треугольнике {A}{B}{C} угол {A} = {a}°, "
                    "угол {B} = {b}°. Найдите угол {C}."
                )
            }),
            "solution_template": forms.Textarea(attrs={
                "rows": 6,
                "placeholder": (
                    "Например: Так как сумма углов треугольника равна 180°, "
                    "то угол {C} = 180° - {a}° - {b}° = {result}°."
                )
            }),
            "source": forms.TextInput(attrs={
                "placeholder": "Например: Атанасян"
            }),
            "source_number": forms.TextInput(attrs={
                "placeholder": "Например: №234"
            }),
            "custom_generator_name": forms.TextInput(attrs={
                "placeholder": "Служебное поле"
            }),
            "tikz_template": forms.Textarea(attrs={
                "rows": 6,
                "style": "font-family: Consolas, monospace;",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["params"].initial = json.dumps(
                self.instance.params or {},
                ensure_ascii=False,
                indent=2
            )

        self.fields["task_type"].required = False
        self.fields["task_type"].initial = "template_formula"

        self.fields["formula"].help_text = (
            "Выбери готовую формулу. Например: triangle_angle_sum = 180 - a - b."
        )

    def _parse_csv(self, value):
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    def _build_numeric_params(self):
        names = self._parse_csv(self.cleaned_data.get("numeric_param_names", ""))
        number_from = self.cleaned_data.get("number_from")
        number_to = self.cleaned_data.get("number_to")
        number_step = self.cleaned_data.get("number_step") or 1

        result = {}

        if not names:
            return result

        if number_from is None or number_to is None:
            raise forms.ValidationError(
                "Если указаны числовые параметры, заполни поля 'От' и 'До'."
            )

        if number_step <= 0:
            raise forms.ValidationError("Шаг должен быть больше 0.")

        if number_from > number_to:
            raise forms.ValidationError("'От' не может быть больше 'До'.")

        values = list(range(number_from, number_to + 1, number_step))

        for name in names:
            result[name] = values

        return result

    def _build_letter_params(self):
        use_letters = self.cleaned_data.get("use_letter_params")

        if not use_letters:
            return {}

        names = self._parse_csv(self.cleaned_data.get("letter_param_names", ""))
        upper = self._parse_csv(self.cleaned_data.get("uppercase_letters", ""))
        lower = self._parse_csv(self.cleaned_data.get("lowercase_letters", ""))

        result = {}

        if not names:
            return result

        for name in names:
            if name[0].isupper():
                result[name] = upper
            else:
                result[name] = lower

        return result

    def clean_params(self):
        raw = self.cleaned_data.get("params", "")

        if isinstance(raw, dict):
            return raw

        raw = str(raw or "").strip()

        if not raw:
            return {}

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Ошибка JSON: {e}")

        if not isinstance(parsed, dict):
            raise forms.ValidationError("JSON должен быть объектом.")

        for key, value in parsed.items():
            if not isinstance(value, list):
                raise forms.ValidationError(
                    f"Параметр '{key}' должен быть списком."
                )
            if not value:
                raise forms.ValidationError(
                    f"Параметр '{key}' не должен быть пустым."
                )

        return parsed

    def clean(self):
        cleaned_data = super().clean()

        task_template = cleaned_data.get("task_template")
        formula = cleaned_data.get("formula")
        params = cleaned_data.get("params") or {}

        cleaned_data["task_type"] = "template_formula"
        cleaned_data["custom_generator_name"] = ""
        cleaned_data["tikz_template"] = cleaned_data.get("tikz_template") or ""

        auto_params = {}

        try:
            auto_params.update(self._build_numeric_params())
            auto_params.update(self._build_letter_params())
        except forms.ValidationError as e:
            self.add_error("params", e)

        if auto_params:
            params.update(auto_params)

        cleaned_data["params"] = params

        if not task_template:
            self.add_error("task_template", "Введите текст задачи.")

        if not params:
            self.add_error(
                "numeric_param_names",
                "Добавь хотя бы один параметр, например: a, b."
            )

        if not formula:
            self.add_error(
                "formula",
                "Выбери формулу для вычисления ответа."
            )

        return cleaned_data