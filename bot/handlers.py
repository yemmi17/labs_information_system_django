import logging
import re

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import (
    keyboard_after_chain,
    keyboard_choose_f1,
    keyboard_choose_f2,
    keyboard_choose_f3,
    keyboard_start,
    parse_function_id,
)
from bot.states import ChainStates
from mini_case.evaluate import EvalErr, evaluate, format_chain_readable

router = Router(name="case-bot")

_FLOAT_RE = re.compile(r"^[-+]?(?:\d+[\.,]\d*|\d*[\.,]\d+|\d+)(?:[eE][-+]?\d+)?$")


def _parse_x(text: str) -> float | None:
    t = text.strip().replace(",", ".")
    if not _FLOAT_RE.match(t):
        return None
    try:
        return float(t)
    except ValueError:
        return None


HELP_TEXT = (
    "Модель: **y = F₁(F₂(F₃(x)))** — сначала к x применяется F₃, затем F₂, затем F₁.\n\n"
    "Доступные функции:\n"
    "• √x — корень; ошибка, если на входе отрицательное число.\n"
    "• 1/x — обратное; ошибка при нуле.\n"
    "• e^x — экспонента; область определения — все вещественные.\n\n"
    "Кнопки:\n"
    "• **Собрать цепочку** — по шагам выбрать F₃, F₂, F₁.\n"
    "• После сборки введите число **x** сообщением.\n"
    "• **Пересобрать цепочку** — начать выбор заново.\n"
    "• **Справка** — этот текст."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Мини-CASE: композиция трёх функций из набора {√x, 1/x, e^x}.\n\n"
        "Нажмите кнопку ниже, чтобы задать F₃, F₂ и F₁.",
        reply_markup=keyboard_start(),
        parse_mode="Markdown",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="Markdown")


@router.callback_query(F.data == "action:help")
async def cb_help(callback: CallbackQuery) -> None:
    await callback.message.answer(HELP_TEXT, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "action:build")
async def cb_build(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ChainStates.choosing_f3)
    await callback.message.edit_text(
        "Шаг **1/3**: выберите **F₃** — первую функцию, применяемую к x.",
        reply_markup=keyboard_choose_f3(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "action:rebuild")
async def cb_rebuild(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ChainStates.choosing_f3)
    await callback.message.answer(
        "Шаг **1/3**: выберите **F₃**.",
        reply_markup=keyboard_choose_f3(),
        parse_mode="Markdown",
    )
    await callback.answer("Цепочка сброшена")


@router.callback_query(F.data.startswith("f3:"))
async def cb_f3(callback: CallbackQuery, state: FSMContext) -> None:
    fid = parse_function_id(callback.data.split(":", 1)[1])
    if fid is None:
        await callback.answer("Неизвестная функция", show_alert=True)
        return
    await state.update_data(f3=fid)
    await state.set_state(ChainStates.choosing_f2)
    await callback.message.edit_text(
        "Шаг **2/3**: выберите **F₂**.",
        reply_markup=keyboard_choose_f2(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("f2:"))
async def cb_f2(callback: CallbackQuery, state: FSMContext) -> None:
    fid = parse_function_id(callback.data.split(":", 1)[1])
    if fid is None:
        await callback.answer("Неизвестная функция", show_alert=True)
        return
    await state.update_data(f2=fid)
    await state.set_state(ChainStates.choosing_f1)
    await callback.message.edit_text(
        "Шаг **3/3**: выберите **F₁**.",
        reply_markup=keyboard_choose_f1(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("f1:"))
async def cb_f1(callback: CallbackQuery, state: FSMContext) -> None:
    fid = parse_function_id(callback.data.split(":", 1)[1])
    if fid is None:
        await callback.answer("Неизвестная функция", show_alert=True)
        return
    data = await state.get_data()
    f3 = data.get("f3")
    f2 = data.get("f2")
    if f3 is None or f2 is None:
        await state.clear()
        await callback.message.edit_text("Сессия устарела. Нажмите /start.")
        await callback.answer()
        return
    await state.update_data(f1=fid)
    await state.set_state(ChainStates.waiting_x)
    readable = format_chain_readable(f3, f2, fid)
    await callback.message.edit_text(
        f"Цепочка: `{readable}`\n\nВведите **x** числом (можно с запятой).",
        parse_mode="Markdown",
    )
    await callback.message.answer(
        "Дальше: пришлите значение x. Кнопки:",
        reply_markup=keyboard_after_chain(),
    )
    await callback.answer()


@router.message(ChainStates.waiting_x, F.text)
async def on_x(message: Message, state: FSMContext) -> None:
    x_val = _parse_x(message.text or "")
    if x_val is None:
        await message.reply("Введите одно вещественное число, например `1` или `-0,5`.", parse_mode="Markdown")
        return
    data = await state.get_data()
    f3, f2, f1 = data.get("f3"), data.get("f2"), data.get("f1")
    if not (f3 and f2 and f1):
        await state.clear()
        await message.reply("Цепочка не задана. Нажмите /start.")
        return
    result = evaluate(x_val, f3, f2, f1)
    readable = format_chain_readable(f3, f2, f1)
    if isinstance(result, EvalErr):
        await message.reply(
            f"{readable}\n"
            f"x = `{x_val}`\n\n"
            f"Ошибка на шаге **{result.step}** (функция {result.function_label}): "
            f"{result.detail}",
            parse_mode="Markdown",
        )
        return
    await message.reply(
        f"{readable}\n" f"x = `{x_val}`\n\n" f"**y** = `{result.value}`",
        parse_mode="Markdown",
    )


@router.message(
    StateFilter(ChainStates.choosing_f3, ChainStates.choosing_f2, ChainStates.choosing_f1),
    F.text,
)
async def nag_choose_buttons(message: Message) -> None:
    await message.reply("Сейчас нужно выбрать функцию **кнопкой** под предыдущим сообщением.")


@router.message()
async def fallback(message: Message, state: FSMContext) -> None:
    st = await state.get_state()
    if st is None:
        await message.reply("Нажмите /start, чтобы открыть меню с кнопками.")
    logging.getLogger(__name__).debug("unhandled message state=%s", st)
