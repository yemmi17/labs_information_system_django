#!/usr/bin/env python
# -*- coding: cp1251 -*-
"""
================================================================================
manage.py
--------------------------------------------------------------------------------
Утилита запуска команд Django для управления проектом.
Файл отвечает за настройку переменной окружения и запуск административных задач.

Изменение выполнено: GitHub Copilot, 18.04.2026
Причина: добавить разъяснения назначения скрипта и комментарии.
================================================================================
"""
import os
import sys


def main():
    """Запускает административные команды Django через execute_from_command_line."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firm_directory.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
