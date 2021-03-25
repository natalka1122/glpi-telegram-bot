"""Login proccess
"""
import logging
from aiogram.dispatcher import FSMContext
import bot.app.core as core
from bot.usersession import UserSession
from bot.glpi_api import GLPIError
from bot.app.bot_state import Form
from bot.app.keyboard import select_command, no_keyboard


async def onboarding_start(user_id: int) -> None:
    """
    Conversation's entry point
    """
    logging.info("%d started onboarding", user_id)
    # Set state
    await Form.to_enter_login.set()
    await core.bot.send_message(
        user_id,
        "Добрый день. Вас приветствует бот для быстрой подачи заявок в службу техподдержки. Введите Ваш логин в системе",
        reply_markup=no_keyboard,
    )


async def process_cancel(user_id: int, state: FSMContext, info_text: str = "") -> None:
    """Reset state

    Args:
        user_id (int): telegram user id that issued command
    """
    logging.info("User ID %d reset state", user_id)
    await UserSession(user_id=user_id).destroy(state=state)
    # await state.finish()
    if len(info_text) > 0:
        await core.bot.send_message(user_id, info_text)


async def process_to_enter_login(user_id: int, login: str, state: FSMContext) -> None:
    """
    Process user login
    """
    logging.info("%d in to_enter_login", user_id)

    await UserSession(user_id=user_id).create(state=state, login=login)

    await Form.to_enter_password.set()
    await core.bot.send_message(user_id, "Введите Ваш пароль", reply_markup=no_keyboard)


async def process_to_enter_password(
    user_id: int, password: str, state: FSMContext
) -> None:
    """
    Process user password
    """
    try:
        await UserSession(user_id=user_id).create(state=state, password=password)
    except GLPIError as err:
        logging.info(
            "User ID %d tried to login to glpi. Error: %s", user_id, err)
        await process_cancel(
            user_id,
            state,
            "Неправильная пара логин/пароль. Давайте попробуем еще раз. Введите /start",
        )
        return
    logging.info("User ID %d has logged in to glpi", user_id)
    await Form.logged_in.set()
    await core.bot.send_message(user_id, "Отлично, теперь нас есть о чём поговорить!", reply_markup=select_command)
