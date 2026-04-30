import json
import string

from django import forms
from .models import Task


TASK_TYPE_HELP = {
    "theory": "Теоретический вопрос или определение. Параметры и формула не нужны.",
    "template_only": "Шаблонная задача без вычислительной формулы. Можно использовать параметры.",
    "template_formula": "Шаблонная задача с параметрами и формулой. Нужно заполнить параметры и выбрать формулу.",
    "proof": "Задача на доказательство. Обычно параметры и формула не нужны.",
    "geometry_tikz": "Геометрическая задача с чертежом TikZ. Параметры и формула — по необходимости.",
    "custom_generator": "Особая задача, которая генерируется Python-функцией. Нужно указать имя генератора.",
}


class TaskAdminForm(forms.ModelForm):
    params = forms.CharField(
        label="Параметры (JSON)",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 6,
            "style": "font-family: Consolas, monospace;",
            "placeholder": '{"a": [4, 5, 6], "h": [3, 4, 5]}'
        }),
        help_text=(
            "Продвинутый режим. Можно оставить пустым, если используешь поля ниже для автосборки параметров."
        ),
    )

    # -------------------------
    # Числовые параметры
    # -------------------------
    numeric_param_names = forms.CharField(
        label="Имена числовых параметров",
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Например: a, h"
        }),
        help_text="Укажи имена переменных через запятую, которые используются в тексте задачи."
    )

    number_from = forms.IntegerField(
        label="Числа: от",
        required=False,
        help_text="Начальное значение диапазона"
    )

    number_to = forms.IntegerField(
        label="Числа: до",
        required=False,
        help_text="Конечное значение диапазона"
    )

    number_step = forms.IntegerField(
        label="Числа: шаг",
        required=False,
        initial=1,
        help_text="Шаг диапазона"
    )

    # -------------------------
    # Буквенные параметры
    # -------------------------
    use_letter_params = forms.BooleanField(
        label="Заменять буквы",
        required=False,
        initial=False
    )

    letter_param_names = forms.CharField(
        label="Имена буквенных параметров",
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Например: A, P, Q, line"
        }),
        help_text="Укажи имена буквенных переменных через запятую."
    )

    uppercase_letters = forms.CharField(
        label="Большие буквы",
        required=False,
        initial="A,B,C,D,M,N,K,L,P,Q,R,S,T",
        widget=forms.TextInput(attrs={
            "placeholder": "A,B,C,D,M,N,K,L"
        }),
        help_text="Используются для точек и вершин."
    )

    lowercase_letters = forms.CharField(
        label="Маленькие буквы",
        required=False,
        initial="a,b,c,d,m,n,k,l,p,q,r,s,t",
        widget=forms.TextInput(attrs={
            "placeholder": "a,b,c,d,m,n,k,l"
        }),
        help_text="Используются для прямых, лучей и т.п."
    )

    class Meta:
        model = Task
        fields = "__all__"
        widgets = {
            "task_template": forms.Textarea(attrs={
                "rows": 6,
                "placeholder": "Например: Найдите площадь треугольника с основанием {a} см и высотой {h} см."
            }),
            "solution_template": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Например: S = 1/2 · {a} · {h} = {result}"
            }),
            "tikz_template": forms.Textarea(attrs={
                "rows": 8,
                "style": "font-family: Consolas, monospace;",
                "placeholder": r"\begin{tikzpicture} ... \end{tikzpicture}"
            }),
            "custom_generator_name": forms.TextInput(attrs={
                "placeholder": "Например: isosceles_triangle_angles"
            }),
            "title": forms.TextInput(attrs={
                "placeholder": "Например: Площадь треугольника"
            }),
            "source": forms.TextInput(attrs={
                "placeholder": "Например: Атанасян"
            }),
            "source_number": forms.TextInput(attrs={
                "placeholder": "Например: №234"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        params_value = self.instance.params if self.instance and self.instance.pk else {}
        self.fields["params"].initial = json.dumps(params_value, ensure_ascii=False, indent=2)

        self.fields["task_type"].help_text = (
            "Выбери тип задачи внимательно:<br>"
            + "<br>".join(
                f"<code>{key}</code> — {value}" for key, value in TASK_TYPE_HELP.items()
            )
        )

        self.fields["formula"].help_text = (
            "Выбирается только для типа <code>template_formula</code>."
        )
        self.fields["custom_generator_name"].help_text = (
            "Заполняется только для типа <code>custom_generator</code>."
        )
        self.fields["tikz_template"].help_text = (
            "Заполняется только если нужен рисунок в LaTeX/TikZ."
        )

    def _parse_csv(self, value: str):
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
                "Если указаны числовые параметры, нужно заполнить поля 'от' и 'до'."
            )

        if number_step <= 0:
            raise forms.ValidationError("Шаг должен быть больше 0.")

        if number_from > number_to:
            raise forms.ValidationError("Поле 'от' не может быть больше поля 'до'.")

        values = list(range(number_from, number_to + 1, number_step))
        if not values:
            raise forms.ValidationError("Не удалось собрать диапазон чисел.")

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

        if not names:
            raise forms.ValidationError(
                "Отмечено 'Заменять буквы', но не указаны имена буквенных параметров."
            )

        result = {}

        for name in names:
            # Простая эвристика:
            # если имя параметра начинается с большой буквы -> даём большие буквы
            # иначе -> маленькие
            if name and name[0].isupper():
                if not upper:
                    raise forms.ValidationError("Список больших букв пуст.")
                result[name] = upper
            else:
                if not lower:
                    raise forms.ValidationError("Список маленьких букв пуст.")
                result[name] = lower

        return result

    def clean_params(self):
        raw = self.cleaned_data.get("params", "").strip()

        if not raw:
            return {}

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Некорректный JSON: {e}")

        if not isinstance(parsed, dict):
            raise forms.ValidationError("Параметры должны быть JSON-объектом, например: {\"a\": [4,5,6]}")

        for key, value in parsed.items():
            if not isinstance(key, str):
                raise forms.ValidationError("Все имена параметров должны быть строками.")
            if not isinstance(value, list):
                raise forms.ValidationError(f"Параметр '{key}' должен содержать список значений.")
            if not value:
                raise forms.ValidationError(f"Параметр '{key}' не должен быть пустым.")

        return parsed

    def clean(self):
        cleaned_data = super().clean()

        task_type = cleaned_data.get("task_type")
        params = cleaned_data.get("params") or {}
        formula = cleaned_data.get("formula")
        custom_generator_name = (cleaned_data.get("custom_generator_name") or "").strip()
        tikz_template = (cleaned_data.get("tikz_template") or "").strip()
        task_template = (cleaned_data.get("task_template") or "").strip()
        solution_template = (cleaned_data.get("solution_template") or "").strip()

        if not task_template:
            self.add_error("task_template", "Поле 'Текст задачи' обязательно.")

        # Если JSON не введён вручную, пробуем собрать его автоматически
        auto_params = {}
        try:
            numeric_params = self._build_numeric_params()
            letter_params = self._build_letter_params()
            auto_params.update(numeric_params)
            auto_params.update(letter_params)
        except forms.ValidationError as e:
            self.add_error("params", e)

        # Если params пустой, но есть автосборка — используем её
        if not params and auto_params:
            cleaned_data["params"] = auto_params
            params = auto_params

        if task_type == "template_formula":
            if not params:
                self.add_error("params", "Для типа 'template_formula' нужны параметры: JSON вручную или поля автогенерации.")
            if not formula:
                self.add_error("formula", "Для типа 'template_formula' нужно выбрать формулу.")

        if task_type == "custom_generator":
            if not custom_generator_name:
                self.add_error(
                    "custom_generator_name",
                    "Для типа 'custom_generator' нужно указать имя кастомного генератора."
                )

        if task_type in ("theory", "proof"):
            # тут параметры не запрещаем жёстко, потому что ты можешь захотеть менять буквы
            pass

        if task_type == "geometry_tikz" and not tikz_template:
            self.add_error(
                "tikz_template",
                "Для типа 'geometry_tikz' желательно заполнить TikZ шаблон."
            )

        if task_type == "template_only" and not solution_template:
            self.add_error(
                "solution_template",
                "Для шаблонной задачи без формулы желательно заполнить решение/ответ."
            )

        return cleaned_data