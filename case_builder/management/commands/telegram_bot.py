import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError

from case_builder.services import evaluate_chain, format_expression, generate_vba, parse_chain


class Command(BaseCommand):
    help = "Runs a simple Telegram polling bot for the lab 11 CASE system."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Validate configuration without polling Telegram.")
        parser.add_argument("--timeout", type=int, default=25, help="Long polling timeout in seconds.")

    def handle(self, *args, **options):
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise CommandError("Set TELEGRAM_BOT_TOKEN before running the bot.")
        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS("Telegram bot configuration is valid."))
            return

        offset = None
        self.stdout.write("Telegram bot started. Use /calc 4 sqrt inv exp")
        while True:
            updates = self._api(token, "getUpdates", {"timeout": options["timeout"], "offset": offset})
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message") or {}
                chat = message.get("chat") or {}
                text = (message.get("text") or "").strip()
                chat_id = chat.get("id")
                if chat_id:
                    self._api(token, "sendMessage", {"chat_id": chat_id, "text": self._reply(text)})
            time.sleep(0.2)

    def _reply(self, text):
        if text.startswith("/start"):
            return "Мини-CASE: отправьте /calc 4 sqrt inv exp. Функции: sqrt, inv, exp."
        if not text.startswith("/calc"):
            return "Команда: /calc <x> <functions>. Пример: /calc 4 sqrt inv exp"
        try:
            parts = text.split(maxsplit=2)
            x_value = float(parts[1])
            chain = parse_chain(parts[2])
        except (IndexError, ValueError) as exc:
            return f"Ошибка ввода: {exc}"

        result = evaluate_chain(x_value, chain)
        if result.ok:
            value_line = f"Результат: {result.value:.6f}"
        else:
            value_line = f"Ошибка на шаге {result.step}: {result.error}"
        return f"{format_expression(chain)}\n{value_line}\n\nVBA:\n{generate_vba(chain)}"

    def _api(self, token, method, params):
        url = f"https://api.telegram.org/bot{token}/{method}"
        data = urlencode(params).encode("utf-8")
        request = Request(url, data=data)
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
