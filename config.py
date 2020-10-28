"""Import the environmental values.
"""

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if TELEGRAM_TOKEN is None:
    print(
        "There is no telegram token. Please provide TELEGRAM_TOKEN in .env file or as environment variable",
        file=sys.stderr,
    )
    sys.exit(1)

GLPI_BASE_URL = os.getenv("GLPI_BASE_URL")
if GLPI_BASE_URL is None:
    print(
        "There is no GPLI API url. Please provide GLPI_BASE_URL in .env file or as environment variable",
        file=sys.stderr,
    )
    sys.exit(1)

DATA_DIR = os.getenv("DATA_DIR")
if DATA_DIR is None:
    DATA_DIR = "data/"
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = DATA_DIR + "db.db"
STATE_FILE = DATA_DIR + "state.json"
LOG_FILENAME = DATA_DIR + "log.txt"

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
    LOG_LEVEL = logging.INFO
