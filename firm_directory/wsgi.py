# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: firm_directory.wsgi
# Назначение: WSGI-точка входа для синхронных production/dev серверов Django.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: прокомментировать глобальную переменную application.
# Первоначальный фрагмент: стандартный WSGI config Django.
# =============================================================================

import os

from django.core.wsgi import get_wsgi_application

# Указываем Django, какой модуль настроек использовать при запуске WSGI.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firm_directory.settings')

# Глобальная переменная: callable-объект, который импортирует WSGI-сервер.
application = get_wsgi_application()
