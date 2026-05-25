from django import forms

from .services import FUNCTIONS


class CaseDesignerForm(forms.Form):
    x_value = forms.FloatField(label="Входное значение x", initial=4)
    chain = forms.MultipleChoiceField(
        label="Последовательность функций",
        choices=[(key, value["label"]) for key, value in FUNCTIONS.items()],
        initial=["sqrt", "inv", "exp"],
        widget=forms.CheckboxSelectMultiple,
        help_text="Функции применяются сверху вниз: первая выбранная функция получает x.",
    )
