"""Main function used are declared here
"""
import logging
from typing import List, Dict

from bot.app.core import bot, create_user_session
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
    try:
        ticket_id = UserSession(user_id).create_ticket(title)
    except StupidError as err:
        logging.error("%s", err)
        await Form.logged_in.set()
        await bot.send_message(user_id, "Ничего не получилось и вылезла ошибка")
        return

    await Form.logged_in.set()
    await bot.send_message(
        user_id,
        "Обращение номер %d создано. Введите /edit для редактирования",
        ticket_id,
    )


async def process_to_select_ticket_number(user_id: int, ticket_id: int) -> None:
    """Edit provided ticket

    Args:
        user_id (int): telegram user id that issued command
        ticket_id (int): ticket id for editing
    """
    try:
        ticket_id = int(ticket_id)
    except ValueError:
        logging.error("Ну кто вводит буквы вместо циферок: %d", ticket_id)
        await Form.logged_in.set()
        await bot.send_message(
            user_id,
            "Ну кто мне тут вводит буквы вместо циферок? Начинай, хулиган, заново!",
        )
        return

    logging.debug("%d process_to_select_ticket_number", user_id)
    try:
        ticket = UserSession(user_id).get_one_ticket(ticket_id)
    except StupidError as err:
        logging.error("%s", err)
        await Form.logged_in.set()
        await bot.send_message(user_id, "Ничего не получилось и вылезла ошибка")
        return

    if ticket is None:
        logging.error("Not found %d", ticket_id)
        await Form.logged_in.set()
        await bot.send_message(user_id, "Тикет не найден. Начинайте заново.")
        return

    logging.debug("Получилось! %s", ticket)
    await Form.logged_in.set()
    await bot.send_message(
        user_id, "Вот ваш тикет: %s. И какое поле в нем мы хотим поменять? ", ticket
    )
    await not_implemented(user_id)


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
