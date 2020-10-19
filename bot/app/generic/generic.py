import sys

import logging
from aiogram import types
from bot.app.core import bot, sessions, create_user_session

print("IMPORT bot.app.generic")


async def start_message(user_id):
    logging.debug('{} /start command'.format(user_id))
    s = await create_user_session(user_id)
    sessions[user_id] = s

async def list_all_tickets(user_id):
    logging.debug('{} /list command'.format(user_id))
    await bot.send_message(user_id, '{} /list command'.format(user_id))


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
