"""Import the environmental values.
"""

import logging
import os
import sys

from dotenv import load_dotenv

WE_ARE_CLOSING = False

load_dotenv()

TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", default="")
if len(TELEGRAM_TOKEN) == 0:
    print(
        "There is no telegram token. Please provide TELEGRAM_TOKEN in .env file or as environment variable",
        file=sys.stderr,
    )
    sys.exit(1)

GLPI_BASE_URL: str = os.getenv("GLPI_BASE_URL", default="")
if len(GLPI_BASE_URL) == 0:
    print(
        "There is no GPLI API url. Please provide GLPI_BASE_URL in .env file or as environment variable",
        file=sys.stderr,
    )
    sys.exit(1)
GLPI_APP_API_KEY: str = os.getenv("GLPI_APP_API_KEY", default="")

CHECK_PERIOD = int(os.getenv("CHECK_PERIOD", default="300"))

_data_dir: str = os.getenv("DATA_DIR", default="data/")
os.makedirs(_data_dir, exist_ok=True)
DB_FILE: str = _data_dir + "db.db"
LOG_FILENAME: str = _data_dir + "log.txt"

_log_level: str = os.getenv("LOG_LEVEL", default="").upper()
LOG_LEVEL: int = logging.INFO
if _log_level == "CRITICAL":
    LOG_LEVEL = logging.CRITICAL
elif _log_level == "ERROR":
    LOG_LEVEL = logging.ERROR
elif _log_level == "WARNING":
    LOG_LEVEL = logging.WARNING
elif _log_level == "INFO":
    LOG_LEVEL = logging.INFO
elif _log_level == "DEBUG":
    LOG_LEVEL = logging.DEBUG
elif _log_level == "NOTSET":
    LOG_LEVEL = logging.NOTSET
