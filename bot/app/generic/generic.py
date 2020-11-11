"""Main function used are declared here
"""
import logging

import typing
from aiogram.dispatcher import FSMContext

from bot.app.core import bot
from bot.app.generic import onboarding

from bot.app.keyboard import no_keyboard, select_urgent_keyboard
from bot.app.bot_state import Form

from bot.app.ticket import show_ticket, urgency_to_int
from bot.usersession import UserSession


async def start_message(user_id: int, state: FSMContext):
    """/start command handler

    Args:
        user_id (int): telegram user id that issued /start command
    """
    user_session = UserSession(user_id=user_id)
    await user_session.create(state=state)
    if user_session.is_logged_in:
        logging.info("User %d already logged in", user_id)
        await Form.logged_in.set()
        await bot.send_message(
            user_id,
            "Вы уж залогинены. Если хотите разлогинится, то введите /logout",
            reply_markup=no_keyboard,
        )
        return
    logging.info("User ID %d is not logged in", user_id)
    await onboarding.onboarding_start(user_id)


async def logout(user_id: int, state: FSMContext) -> None:
    # TODO write docstring
    """[summary]

    Args:
        user_id (int): [description]
        state (FSMContext): [description]
    """
    logging.info("User ID %d is logged out", user_id)
    await state.finish()
    await bot.send_message(
        user_id,
        "Вы разлогинены. Если хотите залогиниться, то введите /start",
        reply_markup=no_keyboard,
    )


async def list_all_tickets(user_id: int, state: FSMContext):
    """/list command handler

    Args:
        user_id (int): telegram user id that issued command
    """
    user_session = UserSession(user_id=user_id)
    await user_session.create(state=state)
    list_tickets: typing.List[typing.Dict] = user_session.get_all_tickets()

    if len(list_tickets) == 0:
        logging.info(
            "User ID %d issued /tickets command and there are no tickets", user_id
        )
        await bot.send_message(user_id, "Список заявок пуст", reply_markup=no_keyboard)
        return

    for current_ticket in list_tickets:
        await show_ticket(
            current_ticket, bot.send_message, user_id, reply_markup=no_keyboard
        )


async def add_new_ticket(user_id: int) -> None:
    """Ask user to enter its login

    Args:
        user_id (int): telegram user id that issued command
    """

    await Form.to_enter_title.set()
    await bot.send_message(
        user_id, "Введите заголовок заявки", reply_markup=no_keyboard
    )


async def process_to_enter_title(user_id: int, title: str, state: FSMContext) -> None:
    """Create new ticket with provided title

    Args:
        user_id (int): telegram user id that issued command
        title (str): title for new ticket
    """
    user_session = UserSession(user_id)
    await user_session.create(state=state)
    await user_session.add_field(key="title", data=title)

    await Form.to_enter_description.set()
    await bot.send_message(
        user_id,
        f'Тема вашей заявки "{title}". Введите описание возникшей проблемы',
        reply_markup=no_keyboard,
    )


async def process_to_enter_description(
    user_id: int, description: str, state: FSMContext
) -> None:
    """Create new ticket with provided title and description

    Args:
        user_id (int): telegram user id that issued command
        description (str): title for new ticket
    """
    user_session = UserSession(user_id)
    await user_session.create(state)
    await user_session.add_field("description", description)

    await Form.to_select_priority.set()
    await bot.send_message(
        user_id, "Выберите приоритет", reply_markup=select_urgent_keyboard
    )


async def process_to_select_priority(
    user_id: int, priority: str, state: FSMContext
) -> None:
    """Create new ticket with provided title, description and priority

    Args:
        user_id (int): telegram user id that issued command
        description (str): title for new ticket
    """
    user_session = UserSession(user_id)
    await user_session.create(state)
    title = await user_session.pop_field(key="title")
    description = await user_session.pop_field(key="description")
    logging.info("title = _%s_ description = _%s_", title, description)
    if len(title) == 0 or len(description) == 0:
        logging.warning(
            "process_to_select_priority(): title = _%s_ description = _%s_",
            title,
            description,
        )
        await Form.logged_in.set()
        await bot.send_message(
            user_id,
            "Заявка не принята. Програма выдала ошибку",
            reply_markup=no_keyboard,
        )
        return
    try:
        priority_int: int = urgency_to_int(priority)
    except KeyError:
        logging.warning(
            "process_to_select_priority(): title = _%s_ description = _%s_ priority = _%s",
            title,
            description,
            priority,
        )
        await Form.logged_in.set()
        await bot.send_message(
            user_id,
            "Заявка не принята. Неправильно выбран приоритет",
            reply_markup=no_keyboard,
        )
        return

    ticket_id = user_session.create_ticket(
        title=title, description=description, urgency=priority_int
    )
    await Form.logged_in.set()
    await bot.send_message(
        user_id,
        f'Заявка "{title}" принята. Номер заявки - {ticket_id}',
        reply_markup=no_keyboard,
    )


async def not_implemented(user_id: int) -> None:
    """Stub function

    Args:
        user_id (int): telegram user id that issued command
    """
    logging.debug("%d not implemented command", user_id)
    await bot.send_message(
        user_id, "{user_id} not implemented command", reply_markup=no_keyboard
    )


# UNKNOWN ==================================================================
async def text_message(user_id):
    """React on something it cannot understand

    Args:
        user_id (int): telegram user id that issued command
    """
    # TODO: Make something great when user input was not understood
    await bot.send_message(
        user_id,
        "К сожалению, наш робот Вас не понял. Попробуйте ещё раз или введите /help",
        reply_markup=no_keyboard,
    )
