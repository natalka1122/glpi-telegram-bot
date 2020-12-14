"""
Different keyboards
"""
import aiogram
from aiogram.types import (
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    # KeyboardButton,
)
from bot.app.ticket import URGENCY

no_keyboard = ReplyKeyboardRemove()

select_urgent_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
)
for value in URGENCY:
    select_urgent_keyboard.insert(URGENCY[value])


def select_approve_refuse(ticket_id: int) -> aiogram.types.InlineKeyboardMarkup:
    approve_solution = InlineKeyboardButton(
        "Подтвердить решение", callback_data=f"approve_solution:{ticket_id}"
    )
    refuse_solution = InlineKeyboardButton(
        "Отклонить решение", callback_data=f"refuse_solution:{ticket_id}"
    )
    return InlineKeyboardMarkup().add(approve_solution, refuse_solution)


def select_repeat_ticket(ticket_id: int) -> aiogram.types.InlineKeyboardMarkup:
    repeat_ticket = InlineKeyboardButton(
        "Повторить заявку", callback_data=f"repeat_ticket:{ticket_id}"
    )
    return InlineKeyboardMarkup().add(repeat_ticket)
