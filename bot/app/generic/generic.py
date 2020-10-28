"""Main function used are declared here
"""
import logging

from aiogram import types
from bot.app.core import bot, create_user_session
from bot.app.state import Form
from bot.app.ticket import show_ticket
from bot.usersession import StupidError, UserSession


async def start_message(user_id: int):
    """/start command handler

    Args:
        user_id (int): telegram user id that issued /start command
    """
    # TODO: Ask logged user if he wants to logout
    logging.debug("%d /start command", user_id)
    await create_user_session(user_id)


async def list_all_tickets(user_id: int):
    """/list command handler

    Args:
        user_id (int): telegram user id that issued command
    """
    logging.debug("%d /list command", user_id)
    list_tickets = UserSession(user_id).get_all_tickets()
    if len(list_tickets) == 0:
        await bot.send_message(user_id, "Нет никаких тикетов")
        return

    for current_ticket in list_tickets:
        ticket_to_print = show_ticket(current_ticket)
        for chunk in ticket_to_print:
            await bot.send_message(user_id, "{}".format(chunk))


async def add_new_ticket(user_id: int) -> None:
    """Ask user to enter its login

    Args:
        user_id (int): telegram user id that issued command
    """
    logging.debug("%d /add command", user_id)

    await Form.to_enter_title.set()
    await bot.send_message(user_id, "Введите, пожалуйста, тему обращения")


async def process_to_enter_title(user_id: int, title: str) -> None:
    """Create new ticket with provided title

    Args:
        user_id (int): telegram user id that issued command
        title (str): title for new ticket
    """
    logging.debug("%d process_to_enter_title", user_id)

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


async def edit_ticket(user_id: int) -> None:
    """Promts for ticket to edit

    Args:
        user_id (int): telegram user id that issued command
    """
    logging.debug("%d /edit command", user_id)
    list_tickets = UserSession(user_id).get_all_tickets()
    if len(list_tickets) == 0:
        await Form.logged_in.set()
        await bot.send_message(user_id, "Нет никаких тикетов")
        return

    for current_ticket in list_tickets:
        await bot.send_message(
            user_id, "Номер: %d Тема: %s", current_ticket["id"], current_ticket["name"]
        )

    await Form.to_select_ticket_number.set()
    await bot.send_message(
        user_id, "Введите, пожалуйста, номер тикета для редактирования"
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
async def text_message(message: types.Message):
    """React on something it cannot understand

    Args:
        message (types.Message): Message user sent
    """
    # TODO: Make something great here
    user_id = message.from_user.id
    text = message.text
    logging.debug("%d Received message unknown message", user_id)
    logging.debug("%d %s", user_id, text)
    await bot.send_message(user_id, "Ничего не понял")
