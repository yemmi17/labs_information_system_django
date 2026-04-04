from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

FunctionId = Literal["sqrt", "inv", "exp"]

FUNC_LABEL_RU: dict[FunctionId, str] = {
    "sqrt": "√x",
    "inv": "1/x",
    "exp": "e^x",
}


@dataclass(frozen=True)
class EvalOk:
    value: float


@dataclass(frozen=True)
class EvalErr:
    step: int
    function_label: str
    detail: str


def _apply_sqrt(v: float) -> tuple[float | None, str | None]:
    if v < 0:
        return None, "аргумент отрицательный; √x определён только при x ≥ 0"
    return math.sqrt(v), None


def _apply_inv(v: float) -> tuple[float | None, str | None]:
    if v == 0:
        return None, "деление на ноль; 1/x не определён при x = 0"
    return 1.0 / v, None


def _apply_exp(v: float) -> tuple[float | None, str | None]:
    return math.exp(v), None


_APPLY = {
    "sqrt": _apply_sqrt,
    "inv": _apply_inv,
    "exp": _apply_exp,
}


def evaluate(x: float, f3: FunctionId, f2: FunctionId, f1: FunctionId) -> EvalOk | EvalErr:
    """Вычисляет F₁(F₂(F₃(x))) слева направо с проверкой области определения на каждом шаге."""
    order: list[tuple[int, FunctionId]] = [(1, f3), (2, f2), (3, f1)]
    v = x
    for step, fid in order:
        fn = _APPLY[fid]
        res, err = fn(v)
        if err is not None:
            return EvalErr(step=step, function_label=FUNC_LABEL_RU[fid], detail=err)
        assert res is not None
        v = res
    return EvalOk(value=v)


def format_chain_readable(f3: FunctionId, f2: FunctionId, f1: FunctionId) -> str:
    """Читаемая запись композиции: y = F₁(F₂(F₃(x)))."""
    a, b, c = FUNC_LABEL_RU[f1], FUNC_LABEL_RU[f2], FUNC_LABEL_RU[f3]
    return f"y = {a}({b}({c}(x)))"
