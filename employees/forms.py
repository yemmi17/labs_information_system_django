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

from .models import Car, Driver, DriverCar, Employee, Waybill


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


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["brand", "plate_number", "production_year", "fuel_rate_per_km"]


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ["employee"]


class DriverCarForm(forms.ModelForm):
    class Meta:
        model = DriverCar
        fields = ["driver", "car"]


class WaybillForm(forms.ModelForm):
    class Meta:
        model = Waybill
        fields = ["driver", "car", "departure_time", "arrival_time", "start_mileage", "end_mileage"]
        widgets = {
            "departure_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "arrival_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_mileage")
        end = cleaned_data.get("end_mileage")
        departure = cleaned_data.get("departure_time")
        arrival = cleaned_data.get("arrival_time")
        driver = cleaned_data.get("driver")
        car = cleaned_data.get("car")

        if start is not None and end is not None and end < start:
            self.add_error("end_mileage", "Конечный километраж не может быть меньше начального.")
        if departure and arrival and arrival <= departure:
            self.add_error("arrival_time", "Время заезда должно быть позже времени выезда.")
        if driver and car and not DriverCar.objects.filter(driver=driver, car=car).exists():
            self.add_error("car", "Выбранный автомобиль не назначен этому водителю.")
        return cleaned_data
