# -*- coding: cp1251 -*-
"""
================================================================================
employees.models
--------------------------------------------------------------------------------
Модуль описывает модель Employee для хранения информации о сотрудниках.
Каждое свойство модели соответствует полю таблицы базы данных.

Изменение выполнено: GitHub Copilot, 18.04.2026
Причина: добавить комментарии модули и документацию для полей модели.
================================================================================
"""

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

    last_name = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    middle_name = models.CharField("Отчество", max_length=100, blank=True)
    position = models.CharField("Должность", max_length=150)
    address = models.CharField("Адрес", max_length=255)
    work_phone = models.CharField("Рабочий телефон", max_length=50)
    personal_phone = models.CharField("Личный телефон", max_length=50)

    class Meta:
        ordering = ("last_name", "first_name", "middle_name")
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        """Возвращает читаемое строковое представление объекта сотрудника."""
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    def get_absolute_url(self):
        """Возвращает URL-адрес списка сотрудников после сохранения объекта."""
        return reverse("employee_list")
