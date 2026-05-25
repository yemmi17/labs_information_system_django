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


class Counterparty(models.Model):
    """Контрагент для лабораторной работы №7.

    Модель имитирует справочник контрагентов из типовой конфигурации:
    пользователь ведет карточки организаций и проверяет заполненность/дубли ИНН.
    """

    name = models.CharField("Наименование", max_length=200)
    inn = models.CharField("ИНН", max_length=12)
    code = models.CharField("Код", max_length=20, unique=True)
    marked_for_deletion = models.BooleanField("Помечен на удаление", default=False)
    duplicate_note = models.CharField("Комментарий проверки", max_length=255, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Изменен", auto_now=True)

    class Meta:
        ordering = ("name", "code")
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"

    def __str__(self):
        return f"{self.name} ({self.inn})"

    @property
    def is_inn_valid(self):
        """Возвращает True для непустого ИНН длиной 10 или 12 цифр."""
        return self.inn.isdigit() and len(self.inn) in (10, 12)
