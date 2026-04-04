import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from bot.handlers import router


def _load_env() -> None:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")


def _http_timeout_seconds() -> float:
    raw = os.getenv("TELEGRAM_HTTP_TIMEOUT", "60").strip()
    try:
        return max(10.0, float(raw))
    except ValueError:
        return 60.0


def _build_aiohttp_session() -> AiohttpSession:
    """
    Поддержка TELEGRAM_PROXY для сетей, где api.telegram.org недоступен напрямую.
    Нужен пакет aiohttp-socks (см. requirements.txt).
    """
    proxy = os.getenv("TELEGRAM_PROXY", "").strip() or None
    timeout = _http_timeout_seconds()
    return AiohttpSession(proxy=proxy, timeout=timeout)


async def main() -> None:
    _load_env()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        logging.error("Не задана переменная окружения BOT_TOKEN (см. docs/03-run.md).")
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    session = _build_aiohttp_session()
    if session.proxy:
        logging.info("Используется прокси для Bot API (TELEGRAM_PROXY).")

    bot = Bot(
        token=token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
