# coding: utf-8

"""Import the environmental values.
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LOG_FILENAME = os.getenv("LOG_FILENAME")
SKIT_BASE_URL = os.getenv("SKIT_BASE_URL")

db_dir = os.getenv("DATABASE")
os.makedirs(db_dir, exist_ok=True)
DB_FILE = db_dir + "db.db"
STATE_FILE = db_dir + "state.json"

log_level = os.getenv("LOG_LEVEL").upper()
if log_level == "CRITICAL":
    LOG_LEVEL = logging.CRITICAL
elif log_level == "ERROR":
    LOG_LEVEL = logging.ERROR
elif log_level == "WARNING":
    LOG_LEVEL = logging.WARNING
elif log_level == "INFO":
    LOG_LEVEL = logging.INFO
elif log_level == "DEBUG":
    LOG_LEVEL = logging.DEBUG
elif log_level == "NOTSET":
    LOG_LEVEL = logging.NOTSET
else:
    print("Wrong log_level: {}".format(log_level))
    LOG_LEVEL = logging.NOTSET
