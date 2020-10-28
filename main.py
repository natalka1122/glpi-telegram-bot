# coding: utf-8

"""Main exec file for telegram bot.
"""

import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from bot.app.core import dp
from bot.app.generic import generic, onboarding
from bot.app.state import Form


# TODO add /help
# TODO add /cancel

@dp.message_handler(commands=["start"], state="*")
async def start_message(message: types.Message):
    """Reacts on /start command in every state"""
    logging.info("%d", message.from_user.id)
    await generic.start_message(message.from_user.id)


# ONBOARDING
# =======================================================
# TODO add logout process

@dp.message_handler(state=Form.to_enter_login)
async def process_to_enter_login(message: types.Message, state: FSMContext):
    """Reacts on every text entered with the state Form.to_enter_login"""
    logging.info("%d", message.from_user.id)
    await onboarding.process_to_enter_login(message, state)


@dp.message_handler(state=Form.to_enter_password)
async def to_enter_password(message: types.Message, state: FSMContext):
    """Reacts on every text entered with the state Form.to_enter_password"""
    logging.info("%d", message.from_user.id)
    await onboarding.process_to_enter_password(message, state)


# TICKETS
# =======================================================


@dp.message_handler(commands=["list"], state=Form.logged_in)
async def list_all_tickets(message: types.Message):
    """Reacts on /list command for logged user"""
    logging.info("%d", message.from_user.id)
    await generic.list_all_tickets(message.from_user.id)


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
