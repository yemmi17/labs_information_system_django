# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: employees.urls
# Назначение: маршрутизация HTTP-запросов приложения employees.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: добавить комментарии к каждому маршруту.
# Первоначальный фрагмент: urlpatterns со списком path().
# =============================================================================

from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views


# Глобальная переменная: список маршрутов URL, обрабатываемых приложением employees.
urlpatterns = [
    # Главная страница лабораторного приложения.
    path("", views.home, name="home"),
    # Страница входа пользователя по логину и паролю.
    path("login/", views.login_view, name="login"),
    # Стандартный выход Django с редиректом из настроек LOGOUT_REDIRECT_URL.
    path("logout/", LogoutView.as_view(), name="logout"),
    # Публичный и авторизованный список сотрудников.
    path("employees/", views.employee_list, name="employee_list"),
    # Создание сотрудника; серверная проверка прав находится во view.
    path("employees/add/", views.employee_create, name="employee_create"),
    # Редактирование сотрудника по первичному ключу pk.
    path("employees/<int:pk>/edit/", views.employee_update, name="employee_update"),
    # Удаление сотрудника по первичному ключу pk после подтверждения.
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    path("materials/", views.material_list, name="material_list"),
    path("materials/add/", views.material_create, name="material_create"),
    path("materials/print/", views.material_print_report, name="material_print_report"),
]
