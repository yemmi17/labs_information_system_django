# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: firm_directory.settings
# Назначение: централизованные настройки Django-проекта.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: прокомментировать глобальные переменные конфигурации.
# Первоначальный фрагмент: стандартный settings.py Django 6.0.4.
# =============================================================================

from pathlib import Path

# Корневая директория проекта, используется для построения абсолютных путей.
BASE_DIR = Path(__file__).resolve().parent.parent


# Быстрые настройки для разработки. Не использовать в production без проверки.
# Секретный ключ Django, необходим для подписи данных сессий и CSRF.
SECRET_KEY = 'django-insecure-99m(8ci@#q!19$^ck7)_%%n_op#tw8yql*0d9c5o-sc3^x_#%#'

# Включение режима отладки в процессе разработки.
DEBUG = True

# Список хостов, допустимых для обработки запросов.
ALLOWED_HOSTS = []


# Глобальная переменная: приложения Django, активированные в проекте.
INSTALLED_APPS = [
    # Встроенная административная панель Django.
    'django.contrib.admin',
    # Встроенная система пользователей, групп и прав.
    'django.contrib.auth',
    # Служебная таблица типов содержимого для прав доступа и моделей.
    'django.contrib.contenttypes',
    # Поддержка серверных пользовательских сессий.
    'django.contrib.sessions',
    # Поддержка одноразовых пользовательских сообщений.
    'django.contrib.messages',
    # Поддержка статических файлов CSS/JS/изображений.
    'django.contrib.staticfiles',
    # Пользовательское приложение справочника сотрудников.
    'employees.apps.EmployeesConfig',
    # Приложение мини-CASE системы для лабораторной работы №11.
    'case_builder.apps.CaseBuilderConfig',
]

# Глобальная переменная: middleware, которые обрабатывают HTTP-запросы и ответы.
MIDDLEWARE = [
    # Базовые security-заголовки Django.
    'django.middleware.security.SecurityMiddleware',
    # Чтение и запись пользовательских сессий.
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Общая обработка запросов, включая нормализацию URL.
    'django.middleware.common.CommonMiddleware',
    # Защита POST-форм от CSRF-атак.
    'django.middleware.csrf.CsrfViewMiddleware',
    # Привязка request.user к текущей сессии.
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Передача flash-сообщений между запросами.
    'django.contrib.messages.middleware.MessageMiddleware',
    # Защита от clickjacking через X-Frame-Options.
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Корневой модуль URL-конфигурации проекта.
ROOT_URLCONF = 'firm_directory.urls'

# Глобальная переменная: настройки шаблонов Django, включая каталоги поиска HTML-файлов.
TEMPLATES = [
    {
        # Backend определяет движок рендеринга Django templates.
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Дополнительный каталог шаблонов на уровне проекта.
        'DIRS': [BASE_DIR / 'templates'],
        # Разрешает Django искать шаблоны внутри установленных приложений.
        'APP_DIRS': True,
        # Дополнительные параметры движка шаблонов.
        'OPTIONS': {
            # Context processors добавляют стандартные переменные в контекст шаблона.
            'context_processors': [
                # Добавляет объект request в шаблоны.
                'django.template.context_processors.request',
                # Добавляет данные аутентификации пользователя.
                'django.contrib.auth.context_processors.auth',
                # Добавляет пользовательские сообщения.
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Указывает WSGI-приложение для запуска на сервере.
WSGI_APPLICATION = 'firm_directory.wsgi.application'


# Глобальная переменная: настройки базы данных.
# Для данного проекта используется SQLite с файлом в корне проекта.
DATABASES = {
    'default': {
        # Движок SQLite выбран для простой локальной лабораторной установки.
        'ENGINE': 'django.db.backends.sqlite3',
        # Файл базы данных хранится рядом с manage.py.
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Глобальная переменная: валидаторы паролей пользовательских учетных записей.
AUTH_PASSWORD_VALIDATORS = [
    {
        # Запрещает пароли, слишком похожие на данные пользователя.
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Проверяет минимальную длину пароля.
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # Запрещает слишком распространенные пароли.
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Запрещает полностью числовые пароли.
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Глобальная переменная: язык интерфейса и форматирования.
LANGUAGE_CODE = 'ru-ru'

# Глобальная переменная: часовой пояс проекта.
TIME_ZONE = 'Europe/Moscow'

# Глобальная переменная: включает систему переводов Django.
USE_I18N = True

# Глобальная переменная: хранит даты и время с учетом timezone-aware режима.
USE_TZ = True


# Глобальная переменная: URL-префикс статических файлов проекта.
STATIC_URL = 'static/'

# Глобальная переменная: дополнительные директории со статическими файлами.
STATICFILES_DIRS = [BASE_DIR / 'static']

# Глобальная переменная: маршрут входа для login_required.
LOGIN_URL = 'login'

# Глобальная переменная: маршрут после успешного входа.
LOGIN_REDIRECT_URL = 'employee_list'

# Глобальная переменная: маршрут после выхода.
LOGOUT_REDIRECT_URL = 'home'

# Автоматический тип поля для первичных ключей моделей по умолчанию.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
