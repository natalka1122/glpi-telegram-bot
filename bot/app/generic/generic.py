"""Main function used are declared here
"""
import logging
from typing import List, Dict

from bot.app.core import bot, create_user_session
from bot.app.keyboard import select_urgent_keyboard
from bot.app.state import Form
from bot.app.ticket import show_ticket
from bot.usersession import StupidError, UserSession


async def start_message(user_id: int):
    """/start command handler

    Args:
        user_id (int): telegram user id that issued /start command
    """
    try:
        UserSession(user_id)
    except StupidError:
        await create_user_session(user_id)
    else:
        logging.info("User %d already logged in", user_id)
        await Form.logged_in.set()
        await bot.send_message(
            user_id, "Вы уж залогинены. Если хотите разлогинится, то введите /logout"
        )


async def list_all_tickets(user_id: int):
    """/list command handler

    Args:
        user_id (int): telegram user id that issued command
    """
    list_tickets: List[Dict] = UserSession(user_id).get_all_tickets()
    if len(list_tickets) == 0:
        logging.info(
            "User ID %d issued /tickets command and there are no tickets", user_id
        )
        await bot.send_message(user_id, "Список тикетов пуст")
        return

    for current_ticket in list_tickets:
        await show_ticket(current_ticket, bot.send_message, user_id)


async def add_new_ticket(user_id: int) -> None:
    """Ask user to enter its login

    Args:
        user_id (int): telegram user id that issued command
    """
    await Form.to_enter_title.set()
    await bot.send_message(user_id, "Введите заголовок заявки")


async def process_to_enter_title(user_id: int, title: str) -> None:
    """Create new ticket with provided title

    Args:
        user_id (int): telegram user id that issued command
        title (str): title for new ticket
    """
    UserSession(user_id).add_field("title", title)

    await Form.to_enter_description.set()
    await bot.send_message(
        user_id,
        'Тема вашей заявки "{}". Введите описание возникшей проблемы'.format(title),
    )


async def process_to_enter_description(user_id: int, description: str) -> None:
    """Create new ticket with provided title and description

    Args:
        user_id (int): telegram user id that issued command
        description (str): title for new ticket
    """
    UserSession(user_id).add_field("description", description)

    await Form.to_select_priority.set()
    await bot.send_message(
        user_id, "Выберите приоритет", reply_markup=select_urgent_keyboard
    )


async def process_to_select_priority(user_id: int, priority: str) -> None:
    """Create new ticket with provided title, description and priority

    Args:
        user_id (int): telegram user id that issued command
        description (str): title for new ticket
    """
    current_user = UserSession(user_id)
    title = current_user.pop_field("title")
    description = current_user.pop_field("description")
    ticket_id = current_user.create_ticket(title, description, priority)

    await Form.logged_in.set()
    await bot.send_message(
        user_id, 'Заявка "{}" принята. Номер заявки - {}'.format(title, ticket_id)
    )


async def not_implemented(user_id: int) -> None:
    """Stub function

    Args:
        user_id (int): telegram user id that issued command
    """
    logging.debug("%d not implemented command", user_id)
    await bot.send_message(user_id, "%d not implemented command", user_id)


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
    )
