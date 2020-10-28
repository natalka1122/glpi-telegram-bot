"""Some core variable initiations
"""
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage

import config
from bot.app.generic import onboarding
from bot.db.dbhelper import DBHelper

logging.basicConfig(
    level=config.LOG_LEVEL,
    filename=config.LOG_FILENAME,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    filemode="a",
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# sessions = expiringdict.ExpiringDict(max_len=2000, max_age_seconds=60 * 60 * 24)

db_connect = DBHelper(config.DB_FILE)

bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=JSONStorage(config.STATE_FILE))


async def create_user_session(user_id: int) -> None:
    """Initiate user session

    Args:
        user_id (int): telegram user id
    """
    # TODO: handle logged in users who wants to logout
    user_data = db_connect.get_data(user_id)
    logging.debug("create_user_session: user_data = %s", user_data)

    if user_data is None:
        logging.info("%s has no session in db", user_id)
        await onboarding.onboarding_start(user_id)
        return

    logging.info("found user_session. NOT IMPLEMENTED")
    await bot.send_message(
        user_id,
        "Вас приветсвует супер-бот СКИТ.\n"
        "Введите /list, что бы получить список тикетов.\n"
        "Введите /add, что бы создать тикет. Введите /edit, что бы отредактировать тикет",
    )
