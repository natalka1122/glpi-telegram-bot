from config import (
    TELEGRAM_TOKEN,
    LOG_FILENAME,
    LOG_LEVEL,
    DB_FILE,
    SKIT_BASE_URL,
    STATE_FILE,
)

import sys
import logging
import expiringdict
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage
from bot.db.dbhelper import DBHelper
from bot.app.generic import onboarding


logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_FILENAME,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    filemode="w",
)

sessions = expiringdict.ExpiringDict(max_len=2000, max_age_seconds=60 * 60 * 24)

db_connect = DBHelper(DB_FILE)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=JSONStorage(STATE_FILE))


async def create_user_session(user_id):
    user_data = db_connect.get_data(user_id)
    logging.debug("create_user_session: user_data = {}".format(user_data))

    if user_data is None:
        logging.info("{} has no session in db".format(user_id))
        await onboarding.onboarding_start(user_id)
        return
    logging.info("found user_session. NOT IMPLEMENTED")
    await bot.send_message(
        user_id,
        "Вас приветсвует супер-бот СКИТ. Введите /list, что бы получить список тикетов. Введите /add, что бы создать тикет. Введите /edit, что бы отредактировать тикет",
    )
