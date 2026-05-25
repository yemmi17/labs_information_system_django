# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: employees.admin
# Назначение: регистрация модели Employee в административной панели Django.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: описать назначение административного класса и его полей.
# Первоначальный фрагмент: регистрация EmployeeAdmin с list_display/search_fields.
# =============================================================================

from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Настройки отображения сотрудников в админке Django.

    Тип: класс конфигурации ModelAdmin.
    Формальные данные: модель Employee, переданная декоратором admin.register.
    Фактические данные: записи сотрудников из базы данных.
    Условия: административная панель доступна пользователям с staff-правами.
    Результат: таблица сотрудников с выбранными колонками и поиском.
    """

    # Колонки, которые администратор видит в списке сотрудников.
    list_display = ("last_name", "first_name", "middle_name", "position", "work_phone")
    # Поля, по которым Django admin выполняет текстовый поиск.
    search_fields = ("last_name", "first_name", "middle_name", "position", "work_phone", "personal_phone")
