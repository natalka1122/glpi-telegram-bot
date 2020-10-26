import sys

import logging
from aiogram import types
from bot.app.core import bot, sessions, create_user_session
from bot.usersession import UserSession, StupidError
from bot.app.ticket import show_ticket
from bot.app.state import Form


async def start_message(user_id):
    logging.debug('{} /start command'.format(user_id))
    s = await create_user_session(user_id)
    sessions[user_id] = s

async def list_all_tickets(user_id):
    logging.debug('{} /list command'.format(user_id))
    list_tickets = UserSession(user_id).get_all_tickers()
    if len(list_tickets) == 0:
        await bot.send_message(user_id, 'Нет никаких тикетов')
        return
    
    chunks = []
    for current_ticket in list_tickets:
        ticket_to_print = show_ticket(current_ticket)
        for chunk in ticket_to_print:
            await bot.send_message(user_id, '{}'.format(chunk))

async def add_new_ticket(user_id):
    logging.debug('{} /add command'.format(user_id))
    # Set state
    await Form.to_enter_title.set()
    await bot.send_message(user_id, "Введите, пожалуйста, тему обращения")

async def process_to_enter_title(user_id, text):
    logging.debug('{} /add command'.format(user_id))

    try:
        ticket_id = UserSession(user_id).create_ticket(text)
    except StupidError as e:
        logging.error("{}".format(e))
        await Form.logged_in.set()
        await bot.send_message(user_id, "Ничего не получилось и вылезла ошибка")
        return

    # Set state
    await Form.logged_in.set()
    await bot.send_message(user_id, "Обращение номер {} создано. Введите /edit для редактирования".format(ticket_id))

async def edit_ticket(user_id):
    logging.debug('{} /edit command'.format(user_id))
    # Set state
    await Form.to_select_ticket_number.set()
    await bot.send_message(user_id, "Введите, пожалуйста, номер тикета для редактирования")

async def not_implemented(user_id):
    logging.debug('{} not implemented command'.format(user_id))
    await bot.send_message(user_id, '{} not implemented command'.format(user_id))

# UNKNOWN ==================================================================
async def text_message(message):
    user_id = message.from_user.id
    text = message.text
    logging.debug("{} Received message unknown message".format(user_id))
    logging.debug("{} {}".format(user_id, text))
    await bot.send_message(user_id, "Ничего не понял. user_id: {} message: {}".format(user_id, text))
