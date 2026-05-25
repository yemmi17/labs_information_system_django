# Лабораторная работа №11

## Тема

Проектирование элементов CASE-систем.

## Реализация в Django

Мини-CASE система реализована как Django app `case_builder`.

Возможности:

- визуальный выбор цепочки математических функций;
- расчет функции от функции;
- проверка области определения на каждом шаге;
- генерация работоспособного VBA-кода;
- Telegram-интеграция через Django management command.

## Поддерживаемые функции

- `sqrt`: квадратный корень, область определения `x >= 0`;
- `inv`: обратная функция `1 / x`, область определения `x != 0`;
- `exp`: экспонента `Exp(x)`.

## Telegram bot

Токен не хранится в коде. Перед запуском нужно задать переменную окружения:

```bash
set TELEGRAM_BOT_TOKEN=123456:telegram-token
py manage.py telegram_bot
```

Smoke-check без подключения к Telegram:

```bash
set TELEGRAM_BOT_TOKEN=dummy
py manage.py telegram_bot --dry-run
```

Команда в чате:

```text
/calc 4 sqrt inv exp
```

Бот вернет выражение, результат вычисления и VBA-код.

## Проверка результата

```bash
py manage.py test
py manage.py check
py manage.py runserver
```

После запуска открыть `/case/`.
