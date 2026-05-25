from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable


FUNCTIONS: dict[str, dict[str, str]] = {
    "sqrt": {"label": "sqrt(x)", "vba": "Sqr"},
    "inv": {"label": "1 / x", "vba": ""},
    "exp": {"label": "Exp(x)", "vba": "Exp"},
}


@dataclass(frozen=True)
class CaseResult:
    ok: bool
    value: float | None = None
    error: str = ""
    step: int | None = None


def evaluate_chain(x: float, chain: list[str]) -> CaseResult:
    value = x
    for index, function_id in enumerate(chain, start=1):
        try:
            value = _apply_function(function_id, value)
        except ValueError as exc:
            return CaseResult(ok=False, error=str(exc), step=index)
    return CaseResult(ok=True, value=value)


def generate_vba(chain: list[str]) -> str:
    lines = [
        "Function CalculateModel(ByVal x As Double) As Variant",
        "    On Error GoTo DomainError",
        "    Dim value As Double",
        "    value = x",
    ]
    for function_id in chain:
        if function_id == "sqrt":
            lines.extend(
                [
                    "    If value < 0 Then GoTo DomainError",
                    "    value = Sqr(value)",
                ]
            )
        elif function_id == "inv":
            lines.extend(
                [
                    "    If value = 0 Then GoTo DomainError",
                    "    value = 1 / value",
                ]
            )
        elif function_id == "exp":
            lines.append("    value = Exp(value)")
    lines.extend(
        [
            "    CalculateModel = value",
            "    Exit Function",
            "DomainError:",
            '    CalculateModel = "Значение вне области определения функции"',
            "End Function",
        ]
    )
    return "\n".join(lines)


def format_expression(chain: list[str]) -> str:
    expression = "x"
    for function_id in chain:
        label = FUNCTIONS[function_id]["label"]
        expression = label.replace("x", expression)
    return f"y = {expression}"


def parse_chain(raw: str) -> list[str]:
    chain = [item.strip().lower() for item in raw.replace(",", " ").split() if item.strip()]
    if not chain:
        raise ValueError("Укажите хотя бы одну функцию.")
    unknown = [item for item in chain if item not in FUNCTIONS]
    if unknown:
        raise ValueError(f"Неизвестные функции: {', '.join(unknown)}.")
    return chain


def _apply_function(function_id: str, value: float) -> float:
    handlers: dict[str, Callable[[float], float]] = {
        "sqrt": _sqrt,
        "inv": _inv,
        "exp": math.exp,
    }
    return handlers[function_id](value)


def _sqrt(value: float) -> float:
    if value < 0:
        raise ValueError("sqrt(x) определена только при x >= 0.")
    return math.sqrt(value)


def _inv(value: float) -> float:
    if value == 0:
        raise ValueError("1 / x не определена при x = 0.")
    return 1 / value
