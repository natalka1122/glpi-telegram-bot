import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import bot.app.core as core
from bot.usersession import UserSession
from bot.glpi_api import GLPIError

print("IMPORT bot.app.generic.onboarding")

class Form(StatesGroup):
    to_enter_login = State()  # Will be represented in storage as 'Form:to_enter_login'
    to_enter_password = State()  # Will be represented in storage as 'Form:to_enter_password'
    logged_in = State()  # Will be represented in storage as 'Form:logged_in'

async def onboarding_start(user_id):
    """
    Conversation's entry point
    """
    logging.info("{} started onboarding".format(user_id))
    # Set state
    await Form.to_enter_login.set()
    await core.bot.send_message(user_id, "Добрый день. Вас приветсвует супер-бот РТК Скит. Введите Ваш логин в системе")


async def process_to_enter_login(message: types.Message, state: FSMContext):
    """
    Process user login
    """
    user_id = message.from_user.id
    logging.info("{} in to_enter_login".format(user_id))
    async with state.proxy() as data:
        data['login'] = message.text

    await Form.to_enter_password.set()
    await core.bot.send_message(user_id, "Введите Ваш пароль")

async def process_to_enter_password(message: types.Message, state: FSMContext):
    """
    Process user password
    """
    user_id = message.from_user.id
    password = message.text
    logging.info("{} in to_enter_password".format(user_id))
    async with state.proxy() as data:
        if 'login' not in data or not isinstance(data['login'], str) or len(data['login']) == 0 or len(password) == 0:
            logging.warning("Something is terribly wrong during authorisation: user_id = {} first_name = {} last_name = {} data = {} ".format(user_id,
                           message.from_user.first_name,
                           message.from_user.last_name,
                           data))
            await core.bot.send_message(message.from_user.id, "Всё сломалось. Надо начинать заново. Введите /start")
            # Finish conversation
            await state.finish()
            return
        login = data['login']
        logging.debug("Try to login userid {} with login {} password {}".format(user_id, login, password))
        try:
            user_session = UserSession(user_id, login, password)
        except GLPIError:
            logging.debug("{} wrong  login/password".format(user_id))
            await core.bot.send_message(user_id, "Неправильная пара логин/пароль. Давайте попробуем еще раз")
            await onboarding_start(user_id)
            return
        

        logging.debug("user {} logged in".format(user_id))
        await Form.logged_in.set()
        await core.bot.send_message(user_id, "Отлично, теперь нас есть о чём поговорить!")
        await core.create_user_session(user_id)
