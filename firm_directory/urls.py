# -*- coding: cp1251 -*-
"""
================================================================================
firm_directory.urls
--------------------------------------------------------------------------------
URL-конфигурация основного проекта firm_directory.
Содержит маршруты для административной панели и маршруты приложения employees.

Изменение выполнено: GitHub Copilot, 18.04.2026
Причина: добавить описание назначения модуля и контекст маршрутов.
================================================================================
URL configuration for firm_directory project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('employees.urls')),
]
