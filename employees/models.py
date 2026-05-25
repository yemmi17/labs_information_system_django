# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: employees.models
# Назначение: описание структуры данных сотрудника и правил отображения модели.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: добавить все требуемые учебные виды комментариев.
# Первоначальный фрагмент: Django-модель Employee с краткими docstring.
# =============================================================================

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


class Material(models.Model):
    """Материал для лабораторной работы №8 и печатной формы справочника."""

    code = models.CharField("Код", max_length=20, unique=True)
    name = models.CharField("Наименование", max_length=200)
    accounting_account = models.CharField("Счет учета", max_length=20)
    quantity = models.PositiveIntegerField("Количество", default=0)

    class Meta:
        ordering = ("code",)
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def quantity_state(self):
        if self.quantity > 100:
            return "above"
        if self.quantity < 10:
            return "below"
        if self.quantity % 5 == 0:
            return "multiple"
        return "normal"
