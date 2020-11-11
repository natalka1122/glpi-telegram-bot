"""
Different keyboards
"""
from aiogram.types import (
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    # KeyboardButton,
    # InlineKeyboardMarkup,
    # InlineKeyboardButton,
)
from bot.app.ticket import URGENCY

no_keyboard = ReplyKeyboardRemove()

select_urgent_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
)
for value in URGENCY:
    select_urgent_keyboard.insert(URGENCY[value])
