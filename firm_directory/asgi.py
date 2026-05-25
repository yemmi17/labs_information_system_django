# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: firm_directory.asgi
# Назначение: ASGI-точка входа для асинхронных серверов приложения.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: прокомментировать глобальную переменную application.
# Первоначальный фрагмент: стандартный ASGI config Django.
# =============================================================================

import os

from django.core.asgi import get_asgi_application

# Указываем Django, какой модуль настроек использовать при запуске ASGI.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firm_directory.settings')

# Глобальная переменная: callable-объект, который импортирует ASGI-сервер.
application = get_asgi_application()
