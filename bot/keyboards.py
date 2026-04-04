from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from mini_case.evaluate import FUNC_LABEL_RU, FunctionId


def _fid_buttons(prefix: str) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text=FUNC_LABEL_RU["sqrt"], callback_data=f"{prefix}:sqrt"),
        InlineKeyboardButton(text=FUNC_LABEL_RU["inv"], callback_data=f"{prefix}:inv"),
        InlineKeyboardButton(text=FUNC_LABEL_RU["exp"], callback_data=f"{prefix}:exp"),
    ]


def keyboard_choose_f3() -> InlineKeyboardMarkup:
    row = _fid_buttons("f3")
    return InlineKeyboardMarkup(inline_keyboard=[row])


def keyboard_choose_f2() -> InlineKeyboardMarkup:
    row = _fid_buttons("f2")
    return InlineKeyboardMarkup(inline_keyboard=[row])


def keyboard_choose_f1() -> InlineKeyboardMarkup:
    row = _fid_buttons("f1")
    return InlineKeyboardMarkup(inline_keyboard=[row])


def keyboard_after_chain() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Пересобрать цепочку", callback_data="action:rebuild"),
                InlineKeyboardButton(text="Справка", callback_data="action:help"),
            ]
        ]
    )


def keyboard_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Собрать цепочку F₃ → F₂ → F₁", callback_data="action:build")],
            [InlineKeyboardButton(text="Справка", callback_data="action:help")],
        ]
    )


def parse_function_id(raw: str) -> FunctionId | None:
    if raw in ("sqrt", "inv", "exp"):
        return raw  # type: ignore[return-value]
    return None
