"""Init variables
"""
import logging
import sys

import aiogram

import config
import bot.db.dbhelper as dbhelper

logging.basicConfig(
    level=config.LOG_LEVEL,
    filename=config.LOG_FILENAME,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    filemode="a",
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

bot = aiogram.Bot(token=config.TELEGRAM_TOKEN)
dp = aiogram.Dispatcher(bot, storage=dbhelper.DBHelper(config.DB_FILE))
