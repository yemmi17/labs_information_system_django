#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===== Служебный комментарий модуля ==========================================
# Модуль: manage.py
# Назначение: точка входа для административных команд Django.
# Исполнитель изменения: Yemmi
# Дата изменения: 02.05.2026
# Причина изменения: привести комментарии к требованиям лабораторной работы.
# Первоначальный фрагмент: стандартный manage.py Django с кратким docstring.
# =============================================================================
import os
import sys

# test comment

def main():
    """Запускает административные команды Django через execute_from_command_line.

    Тип подпрограммы: функция без пользовательского возвращаемого значения.
    Формальные параметры: отсутствуют.
    Фактические данные: sys.argv содержит команду и аргументы командной строки.
    Условия: переменная окружения DJANGO_SETTINGS_MODULE должна указывать на настройки проекта.
    Возвращает: None, управление передается Django management-команде.
    """
    # Устанавливаем модуль настроек по умолчанию, если он не задан извне.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firm_directory.settings')
    # Пытаемся импортировать стандартный исполнитель команд Django.
    try:
        from django.core.management import execute_from_command_line
    # Если Django не установлен или окружение не активировано, формируем понятную ошибку.
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Передаем Django исходные аргументы командной строки.
    execute_from_command_line(sys.argv)


# Запускаем main() только при прямом вызове файла, а не при импорте модуля.
if __name__ == '__main__':
    main()
