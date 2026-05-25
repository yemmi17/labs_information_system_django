# Справочник сотрудников и мини-CASE система

Учебный Django-проект для лабораторной работы №11.

## Запуск Django

```bash
py manage.py migrate
py manage.py runserver
```

Страница мини-CASE системы:

```text
http://127.0.0.1:8000/case/
```

## Telegram bot

Токен задается только через переменную окружения:

```bash
set TELEGRAM_BOT_TOKEN=123456:telegram-token
py manage.py telegram_bot
```

Smoke-check конфигурации:

```bash
set TELEGRAM_BOT_TOKEN=dummy
py manage.py telegram_bot --dry-run
```

Команда в Telegram:

```text
/calc 4 sqrt inv exp
```

Документация лабораторной: `docs/lab11.md`.
