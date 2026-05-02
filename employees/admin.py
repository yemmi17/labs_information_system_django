# -*- coding: cp1251 -*-
"""
================================================================================
employees.admin
--------------------------------------------------------------------------------
Модуль регистрирует модель Employee в административной панели Django
и настраивает отображение списка и поля поиска.

Изменение выполнено: GitHub Copilot, 18.04.2026
Причина: добавить документацию к административному классу.
================================================================================
"""

from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Настройки отображения сотрудников в админке Django."""

    list_display = ("last_name", "first_name", "middle_name", "position", "work_phone")
    search_fields = ("last_name", "first_name", "middle_name", "position", "work_phone", "personal_phone")
