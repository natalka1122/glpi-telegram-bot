"""Init variables
"""
import sys
import logging
import typing
import aiogram
from aiogram import types
from aiogram.types import base

import config
import bot.db.dbhelper as dbhelper

MAX_MESSAGE_LENGTH = 2000


class Bot(aiogram.Bot):
    """
    Base bot class with careful send_message function
    """

    async def send_message(
        self,
        chat_id: typing.Union[base.Integer, base.String],
        text: base.String,
        parse_mode: typing.Union[base.String, None] = None,
        disable_web_page_preview: typing.Union[base.Boolean, None] = None,
        disable_notification: typing.Union[base.Boolean, None] = None,
        reply_to_message_id: typing.Union[base.Integer, None] = None,
        reply_markup: typing.Union[
            types.InlineKeyboardMarkup,
            types.ReplyKeyboardMarkup,
            types.ReplyKeyboardRemove,
            types.ForceReply,
            None,
        ] = None,
    ) -> types.Message:
        logging.info("type(text) = %s text = %s", type(text), text)
        messages: typing.List[str] = []
        if len(text) < MAX_MESSAGE_LENGTH:
            messages.append(text)
        else:
            buffer: str = ""
            for line in text.split("\n"):
                line = str.strip(line)
                if len(buffer + line) <= MAX_MESSAGE_LENGTH:
                    if len(buffer) == 0:
                        buffer = line
                    else:
                        buffer += "\n" + line
                    continue
                # len(buffer) + line > max_len
                if len(buffer) > 0:
                    messages.append(buffer)
                if len(line) < MAX_MESSAGE_LENGTH:
                    buffer = line
                    continue

                # len(line) > max_len
                buffer = ""
                while len(line) > MAX_MESSAGE_LENGTH:
                    chunk = str.strip(line[:MAX_MESSAGE_LENGTH])
                    if len(chunk) > 0:
                        messages.append(chunk)
                    line = str.strip(line[MAX_MESSAGE_LENGTH:])

                if len(line) > 0:
                    messages.append(line)

            if len(buffer) > 0:
                messages.append(buffer)
        if len(messages) == 0:
            return
        for message in messages[:-1]:
            await super().send_message(
                chat_id,
                message,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                reply_markup=None,
            )
        return await super().send_message(
            chat_id,
            messages[-1],
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )


formatter: logging.Formatter = logging.Formatter(
    fmt="%(asctime)s [%(filename)15s:%(lineno)4s - %(funcName)20s() ] - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
handler_stdout: logging.Handler = logging.StreamHandler(sys.stdout)
handler_stdout.setFormatter(formatter)
handler_file: logging.Handler = logging.FileHandler(
    filename=config.LOG_FILENAME, mode="a"
)
handler_file.setFormatter(formatter)
logging.getLogger().setLevel(config.LOG_LEVEL)
logging.getLogger().addHandler(handler_stdout)
logging.getLogger().addHandler(handler_file)

# TODO delete after 15.12.2020
# logging.basicConfig(
#     level=config.LOG_LEVEL,
#     filename=config.LOG_FILENAME,
#     format="%(asctime)s - %(message)s",
#     datefmt="%d-%b-%y %H:%M:%S",
#     filemode="a",
# )
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


bot = Bot(token=config.TELEGRAM_TOKEN)
dp = aiogram.Dispatcher(bot, storage=dbhelper.DBHelper(config.DB_FILE))
