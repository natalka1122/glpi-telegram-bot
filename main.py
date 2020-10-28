"""
Main exec file for telegram bot.
"""

import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from bot.app.core import dp
from bot.app.generic import generic, onboarding
from bot.app.state import Form


# TODO add /help
# TODO add /cancel
# TODO add logout process


@dp.message_handler(commands=["start"], state="*")
async def start_message(message: types.Message, state: FSMContext) -> None:
    """Reacts on /start command in every state"""
    user_id: int = message.from_user.id
    current_state: Union[str, None] = await state.get_state()
    logging.info("User ID %d issued /start command. State: %s", user_id, current_state)

    await generic.start_message(user_id)


# ONBOARDING
# =======================================================


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Form.to_enter_login)
async def process_to_enter_login(message: types.Message, state: FSMContext) -> None:
    """Reacts on every text entered with the state Form.to_enter_login"""
    user_id: int = message.from_user.id
    text: str = message.text
    current_state: Union[str, None] = await state.get_state()
    logging.info(
        "User ID %d provided login: '%s'. State: %s", user_id, text, current_state
    )

    if message.is_command():
        await onboarding.process_cancel(
            user_id,
            state,
            "Что-то пошло не так? Давайте попробуем начать сначала. Введите /start",
        )
        return

    await onboarding.process_to_enter_login(user_id, text, state)


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Form.to_enter_password)
async def to_enter_password(message: types.Message, state: FSMContext) -> None:
    """Reacts on every text entered with the state Form.to_enter_password"""
    user_id: int = message.from_user.id
    text: str = message.text

    current_state: Union[str, None] = await state.get_state()
    logging.info(
        "User ID %d provided password: ***. Status: %s", user_id, current_state
    )

    if message.is_command():
        await onboarding.process_cancel(
            user_id,
            state,
            "Что-то пошло не так? Давайте попробуем начать сначала. Введите /start",
        )
        return

    await onboarding.process_to_enter_password(user_id, text, state)


# TICKETS
# =======================================================


@dp.message_handler(commands=["list"], state=Form.logged_in)
async def list_all_tickets(message: types.Message, state: FSMContext) -> None:
    """Reacts on /list command in every state"""
    user_id: int = message.from_user.id
    current_state: Union[str, None] = await state.get_state()
    logging.info("User ID %d issued /list command. State: %s", user_id, current_state)

    await generic.list_all_tickets(user_id)


@dp.message_handler(commands=["add"], state=Form.logged_in)
async def add_ticket(message: types.Message):
    """Reacts on /add command for logged user"""
    logging.info("%d", message.from_user.id)
    await generic.add_new_ticket(message.from_user.id)


@dp.message_handler(commands=["edit"], state=Form.logged_in)
async def edit_ticket(message: types.Message):
    """Reacts on /edit command for logged user"""
    logging.info("%d", message.from_user.id)
    await generic.edit_ticket(message.from_user.id)


@dp.message_handler(state=Form.to_enter_title)
async def to_enter_title(message: types.Message):
    """Reacts on every text entered with the state Form.to_enter_title"""
    logging.info("%d", message.from_user.id)
    await generic.process_to_enter_title(message.from_user.id, message.text)


@dp.message_handler(state=Form.to_select_ticket_number)
async def to_select_ticket_number(message: types.Message):
    """Default behaviour"""
    logging.info("%d", message.from_user.id)
    await generic.process_to_select_ticket_number(message.from_user.id, message.text)


# UNKNOWN input
# ===============================================================


@dp.message_handler(state="*")
async def text_message(message):
    """Default behaviour"""
    logging.info("%d", message.from_user.id)
    await generic.text_message(message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
    logging.info("GLPI Telegram bot has started")
