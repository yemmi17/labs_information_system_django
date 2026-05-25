# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: employees.forms
# Назначение: описание формы ввода и редактирования данных сотрудника.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: дополнить форму учебными комментариями.
# Первоначальный фрагмент: EmployeeForm на базе Django ModelForm.
# =============================================================================

from django import forms

from .models import Counterparty, Employee


class EmployeeForm(forms.ModelForm):
    """Форма для создания и редактирования сотрудника.

    Тип: класс формы Django ModelForm.
    Формальные данные: пользовательские значения полей модели Employee.
    Фактические данные: request.POST передается во view при создании или редактировании.
    Условия: значения проходят стандартную валидацию Django по типам и max_length модели.
    Результат: валидированный объект формы, способный создать или обновить Employee.
    """

    class Meta:
        """Связывает форму с моделью и явно задает разрешенные поля ввода."""

        # Модель, на основе которой Django строит поля формы.
        model = Employee
        # Явный список полей защищает форму от случайного вывода новых полей модели.
        fields = [
            "last_name",
            "first_name",
            "middle_name",
            "position",
            "address",
            "work_phone",
            "personal_phone",
        ]


class CounterpartyForm(forms.ModelForm):
    """Форма карточки контрагента с серверной проверкой ИНН."""

    class Meta:
        model = Counterparty
        fields = ["name", "code", "inn", "marked_for_deletion", "duplicate_note"]

    def clean_inn(self):
        inn = self.cleaned_data["inn"].strip()
        if not inn:
            raise forms.ValidationError("ИНН должен быть заполнен.")
        if not inn.isdigit() or len(inn) not in (10, 12):
            raise forms.ValidationError("ИНН должен содержать 10 или 12 цифр.")
        return inn
