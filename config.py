"""Import the environmental values.
"""

import logging
import os
import re
import sys
import requests

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
try:
    r = requests.head(GLPI_BASE_URL)
    if r.status_code != 200:
        print(f"GLPI server {GLPI_BASE_URL} seems offline", file=sys.stderr)
        sys.exit(1)
except requests.ConnectionError:
    print(f"GLPI server {GLPI_BASE_URL} seems offline", file=sys.stderr)
    sys.exit(1)
GLPI_TICKET_URL: str = os.getenv("GLPI_TICKET_URL", default="")
if len(GLPI_TICKET_URL) == 0:
    re_glpi_base = re.match(r"^(.*)\/\/(.*)\/apirest\.php(.*)$", GLPI_BASE_URL)
    if re_glpi_base is None:
        print(
            "There is no GLPI_TICKET_URL url. Please provide GLPI_TICKET_URL in .env file or as environment variable",
            file=sys.stderr,
        )
        sys.exit(1)
    GLPI_TICKET_URL = f"{re_glpi_base.group(1)}//{re_glpi_base.group(2)}/front/ticket.form.php?id="
GLPI_APP_API_KEY: str = os.getenv("GLPI_APP_API_KEY", default="")

CHECK_PERIOD = int(os.getenv("CHECK_PERIOD", default="30"))

_data_dir: str = os.getenv("DATA_DIR", default="/data/")
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
