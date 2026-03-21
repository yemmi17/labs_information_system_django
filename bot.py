import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.error import NetworkError, TimedOut
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from rbc_rates import CurrencyRate, fetch_rates

CACHE_TTL_MINUTES = 15
SEND_RETRIES = 3


def _help_text() -> str:
    return (
        "Я бот курсов валют.\n\n"
        "Команды:\n"
        "/start - запустить бота\n"
        "/list - показать список доступных валют\n"
        "/rate USD - курс конкретной валюты\n\n"
        "Также можно просто отправить код валюты, например: EUR"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [["/list"], ["/rate USD", "/rate EUR", "/rate CNY"]]
    await _safe_reply_text(
        update,
        _help_text(),
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


async def _get_cached_rates(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, CurrencyRate]:
    rates = context.bot_data.get("rates")
    loaded_at: datetime | None = context.bot_data.get("rates_loaded_at")

    if rates and loaded_at and datetime.now() - loaded_at < timedelta(minutes=CACHE_TTL_MINUTES):
        return rates

    rates = fetch_rates()
    context.bot_data["rates"] = rates
    context.bot_data["rates_loaded_at"] = datetime.now()
    return rates


async def list_currencies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rates = await _get_cached_rates(context)
    codes = sorted(rates.keys())
    msg = "Доступные валюты:\n" + ", ".join(codes)
    await _safe_reply_text(update, msg)


def _format_rate(rate: CurrencyRate) -> str:
    timestamp = rate.timestamp.strftime("%d.%m.%Y %H:%M:%S")
    return (
        f"Курс {rate.code}: {rate.value:.4f} RUB\n"
        f"Источник: {rate.source}\n"
        f"Время обновления: {timestamp}"
    )


async def rate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await _safe_reply_text(update, "Использование: /rate USD")
        return

    code = context.args[0].upper()
    await _send_rate(update, context, code)


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip().upper()
    if len(text) == 3 and text.isalpha():
        await _send_rate(update, context, text)
        return
    await _safe_reply_text(update, "Отправьте 3-буквенный код валюты или используйте /list")


async def _send_rate(update: Update, context: ContextTypes.DEFAULT_TYPE, code: str) -> None:
    rates = await _get_cached_rates(context)
    rate = rates.get(code)
    if not rate:
        await _safe_reply_text(
            update,
            f"Валюта {code} не найдена. Используйте /list для списка доступных валют."
        )
        return

    await _safe_reply_text(update, _format_rate(rate))


async def _safe_reply_text(update: Update, text: str, **kwargs) -> None:
    if not update.message:
        return

    for attempt in range(SEND_RETRIES):
        try:
            await update.message.reply_text(text, **kwargs)
            return
        except (TimedOut, NetworkError):
            if attempt == SEND_RETRIES - 1:
                return
            await asyncio.sleep(1.5 * (attempt + 1))


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Обработанная ошибка: {context.error!r}")


def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Переменная окружения TELEGRAM_BOT_TOKEN не задана.")

    app = (
        Application.builder()
        .token(token)
        .connect_timeout(25.0)
        .read_timeout(25.0)
        .write_timeout(25.0)
        .pool_timeout(25.0)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_currencies))
    app.add_handler(CommandHandler("rate", rate_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(_error_handler)

    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    # Python 3.14+: explicitly create and set the main event loop.
    asyncio.set_event_loop(asyncio.new_event_loop())
    app.run_polling()


if __name__ == "__main__":
    main()
