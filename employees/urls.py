# -*- coding: cp1251 -*-
"""
================================================================================
employees.urls
--------------------------------------------------------------------------------
Модуль конфигурирует маршруты URL для приложения employees.
Каждый путь связывает URL с соответствующим представлением (view).

Изменение выполнено: GitHub Copilot, 18.04.2026
Причина: добавить документацию и пояснения к маршрутам.
================================================================================
"""

from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views


# Список маршрутов URL, обрабатываемых приложением employees.
urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),
]
