import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

RBC_URL = "http://stock.rbc.ru/demo/cb.0/intraday/"
CBR_FALLBACK_URL = "https://www.cbr-xml-daily.ru/daily_json.js"


@dataclass
class CurrencyRate:
    code: str
    value: float
    source: str
    timestamp: datetime


def _normalize_number(raw: str) -> Optional[float]:
    cleaned = raw.replace(" ", "").replace(",", ".")
    if re.fullmatch(r"\d+(?:\.\d+)?", cleaned):
        return float(cleaned)
    return None


def _extract_rate_from_cells(cells: list[str]) -> Optional[float]:
    for cell in reversed(cells):
        value = _normalize_number(cell)
        if value is not None:
            return value
    return None


def fetch_rates_from_rbc(timeout: int = 12) -> Dict[str, CurrencyRate]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(RBC_URL, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rates: Dict[str, CurrencyRate] = {}
    now = datetime.now()

    for row in soup.select("tr"):
        cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
        if not cells:
            continue

        row_text = " ".join(cells)
        code_match = re.search(r"\b[A-Z]{3}\b", row_text)
        if not code_match:
            continue

        code = code_match.group(0)
        rate = _extract_rate_from_cells(cells)
        if rate is None:
            continue

        rates[code] = CurrencyRate(code=code, value=rate, source="RBC", timestamp=now)

    if not rates:
        raise ValueError("Не удалось извлечь курсы валют со страницы РБК.")

    return rates


def fetch_rates_from_cbr_fallback(timeout: int = 12) -> Dict[str, CurrencyRate]:
    response = requests.get(CBR_FALLBACK_URL, timeout=timeout)
    response.raise_for_status()
    data = response.json()

    now = datetime.now()
    rates: Dict[str, CurrencyRate] = {}
    for code, payload in data.get("Valute", {}).items():
        rates[code] = CurrencyRate(
            code=code,
            value=float(payload["Value"]),
            source="CBR-FALLBACK",
            timestamp=now,
        )
    return rates


def fetch_rates() -> Dict[str, CurrencyRate]:
    try:
        return fetch_rates_from_rbc()
    except Exception:
        return fetch_rates_from_cbr_fallback()
