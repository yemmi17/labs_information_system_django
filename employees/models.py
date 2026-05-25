# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: employees.models
# Назначение: описание структуры данных сотрудника и правил отображения модели.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: добавить все требуемые учебные виды комментариев.
# Первоначальный фрагмент: Django-модель Employee с краткими docstring.
# =============================================================================

from decimal import Decimal

from django.db import models
from django.urls import reverse


class Employee(models.Model):
    """Представляет запись сотрудника в базе данных.

    Атрибуты:
        last_name (CharField): фамилия сотрудника.
        first_name (CharField): имя сотрудника.
        middle_name (CharField): отчество сотрудника, необязательно.
        position (CharField): должность сотрудника.
        address (CharField): адрес сотрудника.
        work_phone (CharField): рабочий телефон контактной информации.
        personal_phone (CharField): личный телефон контактной информации.
    """

    # Поле БД: фамилия сотрудника; обязательное значение длиной до 100 символов.
    last_name = models.CharField("Фамилия", max_length=100)
    # Поле БД: имя сотрудника; обязательное значение длиной до 100 символов.
    first_name = models.CharField("Имя", max_length=100)
    # Поле БД: отчество сотрудника; blank=True разрешает пустое значение в форме.
    middle_name = models.CharField("Отчество", max_length=100, blank=True)
    # Поле БД: должность сотрудника; используется в списке и карточке сотрудника.
    position = models.CharField("Должность", max_length=150)
    # Поле БД: адрес сотрудника; показывается только авторизованным пользователям.
    address = models.CharField("Адрес", max_length=255)
    # Поле БД: рабочий телефон; доступен гостю как публичный контакт.
    work_phone = models.CharField("Рабочий телефон", max_length=50)
    # Поле БД: личный телефон; скрыт от гостевого просмотра.
    personal_phone = models.CharField("Личный телефон", max_length=50)

    class Meta:
        """Метаданные модели Employee для ORM и административного интерфейса."""

        # Сортируем сотрудников по ФИО, чтобы список был предсказуемым.
        ordering = ("last_name", "first_name", "middle_name")
        # Единственное читаемое имя модели для интерфейса Django.
        verbose_name = "Сотрудник"
        # Множественное читаемое имя модели для интерфейса Django.
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        """Возвращает читаемое строковое представление объекта сотрудника.

        Тип подпрограммы: метод экземпляра модели.
        Формальные параметры: self содержит текущий объект Employee.
        Фактические данные: поля last_name, first_name и middle_name объекта.
        Условия: строковые поля могут быть пустыми только там, где это разрешено моделью.
        Возвращает: str с ФИО сотрудника без лишних пробелов по краям.
        """
        # Собираем ФИО в одну строку и удаляем крайние пробелы при пустом отчестве.
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    def get_absolute_url(self):
        """Возвращает URL-адрес списка сотрудников после сохранения объекта.

        Тип подпрограммы: метод экземпляра модели.
        Формальные параметры: self содержит текущий объект Employee.
        Фактические данные: именованный маршрут employee_list из employees.urls.
        Условия: маршрут employee_list должен быть зарегистрирован в URLconf.
        Возвращает: str с URL-адресом страницы списка сотрудников.
        """
        # Используем reverse(), чтобы не хардкодить URL и сохранить связность с URLconf.
        return reverse("employee_list")


class Car(models.Model):
    """Справочник автомобилей для лабораторной работы №9."""

    brand = models.CharField("Марка автомобиля", max_length=100)
    plate_number = models.CharField("Гос. номер", max_length=20, unique=True)
    production_year = models.PositiveIntegerField("Год выпуска")
    fuel_rate_per_km = models.DecimalField("Норма расхода литров на 1 км", max_digits=6, decimal_places=3)

    class Meta:
        ordering = ("plate_number",)
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"

    def __str__(self):
        return f"{self.brand} {self.plate_number}"


class Driver(models.Model):
    """Справочник водителей, связанный с сотрудниками."""

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    cars = models.ManyToManyField(Car, through="DriverCar", verbose_name="Автомобили")

    class Meta:
        ordering = ("employee__last_name", "employee__first_name")
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"

    def __str__(self):
        return str(self.employee)


class DriverCar(models.Model):
    """Связь водитель-автомобиль, позволяющая одному водителю иметь несколько машин."""

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name="Водитель")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")

    class Meta:
        unique_together = ("driver", "car")
        verbose_name = "Автомобиль водителя"
        verbose_name_plural = "Автомобили водителей"

    def __str__(self):
        return f"{self.driver} - {self.car}"


class Waybill(models.Model):
    """Документ путевого листа с вычисляемым пробегом и расходом топлива."""

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name="Водитель")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    departure_time = models.DateTimeField("Время выезда")
    arrival_time = models.DateTimeField("Время заезда")
    start_mileage = models.PositiveIntegerField("Начальный километраж")
    end_mileage = models.PositiveIntegerField("Конечный километраж")

    class Meta:
        ordering = ("-departure_time",)
        verbose_name = "Путевой лист"
        verbose_name_plural = "Путевые листы"

    def __str__(self):
        return f"Путевой лист {self.driver} / {self.car}"

    @property
    def distance(self):
        return max(self.end_mileage - self.start_mileage, 0)

    @property
    def fuel_consumption(self):
        return Decimal(self.distance) * Decimal(self.car.fuel_rate_per_km)
