"""Import the environmental values.
"""

import logging
import os
import sys

from dotenv import load_dotenv

WE_ARE_CLOSING = False
CHECK_PERIOD = 20

load_dotenv()

TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN")
if TELEGRAM_TOKEN is None:
    print(
        "There is no telegram token. Please provide TELEGRAM_TOKEN in .env file or as environment variable",
        file=sys.stderr,
    )
    sys.exit(1)

GLPI_BASE_URL: str = os.getenv("GLPI_BASE_URL")
if GLPI_BASE_URL is None:
    print(
        "There is no GPLI API url. Please provide GLPI_BASE_URL in .env file or as environment variable",
        file=sys.stderr,
    )
    sys.exit(1)

_data_dir: str = os.getenv("DATA_DIR", default="/data/")
os.makedirs(_data_dir, exist_ok=True)
DB_FILE: str = _data_dir + "db.db"
STATE_FILE: str = _data_dir + "state.json"
LOG_FILENAME: str = _data_dir + "log.txt"

_log_level: str = os.getenv("LOG_LEVEL", default="").upper()
if _log_level == "CRITICAL":
    LOG_LEVEL: str = logging.CRITICAL
elif _log_level == "ERROR":
    LOG_LEVEL: str = logging.ERROR
elif _log_level == "WARNING":
    LOG_LEVEL: str = logging.WARNING
elif _log_level == "INFO":
    LOG_LEVEL: str = logging.INFO
elif _log_level == "DEBUG":
    LOG_LEVEL: str = logging.DEBUG
elif _log_level == "NOTSET":
    LOG_LEVEL: str = logging.NOTSET
else:
    LOG_LEVEL: str = logging.INFO
