"""Some core variable initiations
"""
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext

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

# db_connect = DBHelper(config.DB_FILE)

bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=DBHelper(config.DB_FILE))


async def create_user_session(user_id: int, state: FSMContext) -> None:
    """Initiate user session

    Args:
        user_id (int): telegram user id
    """
    # TODO: General fix here neededs
    user_data = await state.get_data()
    logging.debug("create_user_session: user_data = %s", user_data)

    if user_data is None:
        logging.info("%s has no session in db", user_id)
        await onboarding.onboarding_start(user_id)
        return

    logging.info("found user_session. NOT IMPLEMENTED")
    await bot.send_message(
        user_id,
        "Вас приветсвует супер-бот СКИТ\n"
        "Введите /tickets, что бы получить список заявок\n"
        "Введите /add, что бы создать заявку",
    )
