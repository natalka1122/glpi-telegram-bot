"""Login proccess
"""
import logging
from aiogram.dispatcher import FSMContext
import bot.app.core as core
from bot.usersession import UserSession
from bot.glpi_api import GLPIError
from bot.app.state import Form


async def onboarding_start(user_id):
    """
    Conversation's entry point
    """
    logging.info("%d started onboarding", user_id)
    # Set state
    await Form.to_enter_login.set()
    await core.bot.send_message(
        user_id,
        "Добрый день. Вас приветсвует супер-бот РТК Скит. Введите Ваш логин в системе",
    )


async def process_cancel(user_id: int, state: FSMContext, info_text: str = "") -> None:
    """Reset state

    Args:
        user_id (int): telegram user id that issued command
    """
    logging.info("User ID %d reset state", user_id)
    await state.finish()
    if len(info_text) > 0:
        await core.bot.send_message(user_id, info_text)


async def process_to_enter_login(user_id: int, login: str, state: FSMContext):
    """
    Process user login
    """
    logging.info("%d in to_enter_login", user_id)

    async with state.proxy() as data:
        data["login"] = login

    await Form.to_enter_password.set()
    await core.bot.send_message(user_id, "Введите Ваш пароль")


async def process_to_enter_password(user_id: int, password: str, state: FSMContext):
    """
    Process user password
    """
    logging.info("%d in to_enter_password", user_id)
    async with state.proxy() as data:
        if (
            "login" not in data
            or not isinstance(data["login"], str)
            or len(data["login"]) == 0
            or len(password) == 0
        ):
            logging.warning(
                "Something is terribly wrong during authorisation: user_id = %d data = %s",
                user_id,
                data,
            )
            await core.bot.send_message(
                user_id,
                "Всё сломалось. Надо начинать заново. Введите /start",
            )
            # Finish conversation
            await state.finish()
            return
        login = data["login"]
        logging.debug(
            "Try to login userid %d with login %s password %s", user_id, login, password
        )
        try:
            UserSession(user_id, login, password)
        except GLPIError:
            logging.debug("%d wrong  login/password", user_id)
            await core.bot.send_message(
                user_id, "Неправильная пара логин/пароль. Давайте попробуем еще раз"
            )
            await onboarding_start(user_id)
            return

        logging.debug("user %d logged in", user_id)
        await Form.logged_in.set()
        await core.bot.send_message(
            user_id, "Отлично, теперь нас есть о чём поговорить!"
        )
        await core.create_user_session(user_id)
