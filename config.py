"""Import the environmental values.
"""

import logging
import os
import sys

from dotenv import load_dotenv

WE_ARE_CLOSING = False

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
GLPI_APP_API_KEY: str = os.getenv("GLPI_APP_API_KEY", "")

CHECK_PERIOD = int(os.getenv("CHECK_PERIOD", "300"))

# GLPI_USE_ADMIN: bool = bool(os.getenv("GLPI_USE_ADMIN", str(False)).lower() != "false")
# if GLPI_USE_ADMIN:
#     GLPI_ADMIN_LOGIN: str = os.getenv("GLPI_ADMIN_LOGIN", "")
#     GLPI_ADMIN_PASSWORD: str = os.getenv("GLPI_ADMIN_PASSWORD", "")
#     GLPI_ADMIN_API_KEY: str = os.getenv("GLPI_ADMIN_API_KEY", "")

_data_dir: str = os.getenv("DATA_DIR", default="/data/")
os.makedirs(_data_dir, exist_ok=True)
DB_FILE: str = _data_dir + "db.db"
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
