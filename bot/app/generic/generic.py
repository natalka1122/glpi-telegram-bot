"""Main function used are declared here
"""
import logging

from typing import Dict
from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.app import keyboard

from bot.app.core import bot
from bot.app.generic import onboarding

from bot.app.keyboard import no_keyboard, select_urgent_keyboard, select_cancel_create, select_command
from bot.app.bot_state import Form

from bot.app.ticket import show_ticket, urgency_to_int
from bot.usersession import StupidError, UserSession
# from bot.app.quote_generator import get_quote
import bot.glpi_api as glpi_api
from config import GLPI_TICKET_URL


async def start_message(user_id: int, state: FSMContext) -> None:
    """/start command handler

    Args:
        user_id (int): telegram user id that issued /start command
        state (FSMContext): state for specific user
    """
    user_session = UserSession(user_id=user_id)
    await user_session.create(state=state)
    if user_session.is_logged_in:
        logging.info("User %d already logged in", user_id)
        await Form.logged_in.set()
        await bot.send_message(
            user_id,
            "Вы ужe залогинены. Если хотите разлогинится, то введите /logout. Что бы увидеть все команды, введите /help",
            reply_markup=select_command,
        )
        return
    logging.info("User ID %d is not logged in", user_id)
    await onboarding.onboarding_start(user_id)


async def help_command(user_id: int) -> None:
    """/help command handler

    Args:
        user_id (int): telegram user id that issued /help command
    """
    await bot.send_message(
        user_id,
        "Вас приветсвует бот для быстрой подачи заявок в службу техподдержки\n"
        # "Введите /Мои заявки, что бы получить список заявок\n"
        # "Введите /add, что бы создать заявку",
    )


async def logout(user_id: int, state: FSMContext) -> None:
    """/logout command handler

    Args:
        user_id (int): telegram user id that issued /logout command
        state (FSMContext): state for specific user
    """
    logging.info("User ID %d is logged out", user_id)
    await state.finish()
    await bot.send_message(
        user_id,
        "Вы разлогинены. Если хотите залогиниться, то введите /start",
        reply_markup=no_keyboard,
    )


async def cancel(user_id: int) -> None:
    """/cancel command handler

    Args:
        user_id (int): telegram user id that issued /cancel command
        state (FSMContext): state for specific user
    """
    await Form.logged_in.set()
    await bot.send_message(user_id, "И снова здравствуйте!", reply_markup=select_command)


async def list_all_tickets(user_id: int, state: FSMContext) -> None:
    """/list command handler

    Args:
        user_id (int): telegram user id that issued command
    """
    user_session = UserSession(user_id=user_id)
    await user_session.create(state=state)
    try:
        list_tickets: Dict[int, Dict] = user_session.get_all_my_tickets(
            open_only=True, full_info=True
        )
    except glpi_api.GLPIError as err:
        logging.error("Ошибка %s", err)
        # TODO Catch error properly
        return

    if len(list_tickets) == 0:
        logging.info(
            "User ID %d issued /tickets command and there are no tickets", user_id
        )
        await bot.send_message(user_id, "Список заявок пуст", reply_markup=select_command)
        return
    logging.info("list_tickets = %s", list_tickets)
    logging.info("list_tickets = %s", list(enumerate(list_tickets)))
    for ticket_id in list_tickets:
        current_ticket = list_tickets[ticket_id]
        try:
            logging.info("current_ticket = %s", current_ticket)
            await bot.send_message(
                chat_id=user_id,
                # text=show_ticket(user_session.get_one_ticket(current_ticket)),
                text=show_ticket(current_ticket),
                reply_markup=select_command,
            )
        except glpi_api.GLPIError as err:
            logging.error("Ошибка %s", err)
            # TODO Catch error properly
            return
        # await show_ticket(
        #     current_ticket, bot.send_message, user_id, reply_markup=no_keyboard
        # )


async def add_new_ticket(user_id: int) -> None:
    """Ask user to enter its login

    Args:
        user_id (int): telegram user id that issued command
    """

    await Form.to_enter_title.set()
    await bot.send_message(
        user_id, "Введите заголовок заявки", reply_markup=select_cancel_create
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
        reply_markup=select_cancel_create,
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
            reply_markup=select_command,
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
            reply_markup=select_command,
        )
        return

    try:
        ticket_id = user_session.create_ticket(
            title=title, description=description, urgency=priority_int
        )
    except StupidError as err:
        message_text: str = f"Произошла неизвестная науке ошибка {err}"
    else:
        # message_text = f'Заявка "{title}" принята. Номер заявки - [{ticket_id}]({GLPI_TICKET_URL}{ticket_id})'
        message_text = f'Заявка "{title}" принята. Номер заявки - <a href="{GLPI_TICKET_URL}{ticket_id}">{ticket_id}</a>'
    logging.info(message_text)
    await bot.send_message(user_id, message_text, reply_markup=select_command)
    await Form.logged_in.set()


async def not_implemented(user_id: int) -> None:
    """Stub function

    Args:
        user_id (int): telegram user id that issued command
    """
    logging.debug("%d not implemented command", user_id)
    await bot.send_message(
        user_id, "{user_id} not implemented command", reply_markup=no_keyboard
    )


async def approve_solution(
    callback_query: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """ Approve solution """
    callback_id: str = callback_query.id
    message_id: int = callback_query.message.message_id
    message_text: str = callback_query.message.text
    user_id: int = callback_query.from_user.id
    ticket_id: int = int(callback_query.data.split(":")[1])
    user_session = UserSession(user_id)
    await user_session.create(state)
    user_session.approve_ticket_solution(ticket_id)
    # ddd= await bot.answer_callback_query(callback_id,text="TEXT",show_alert=True)
    # logging.info("callback done %s", ddd)
    await bot.edit_message_text(
        message_text,
        chat_id=user_id,
        message_id=message_id,
        reply_markup=keyboard.select_repeat_ticket(ticket_id),
    )
    ddd = await bot.answer_callback_query(callback_id)
    logging.info("callback done %s", ddd)


async def repeat_ticket(
    callback_query: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """ Duplicate ticket """
    callback_id: str = callback_query.id
    user_id: int = callback_query.from_user.id
    ticket_id: int = int(callback_query.data.split(":")[1])

    user_session = UserSession(user_id)
    await user_session.create(state)
    ticket: Dict = user_session.get_one_ticket(ticket_id)
    title: str = ticket.get("name", str(None))
    description: str = ticket.get("content", str(None))
    priority_int: int = ticket.get("priority", str(None))
    try:
        ticket_id = user_session.create_ticket(
            title=title, description=description, urgency=priority_int
        )
    except StupidError as err:
        message_text: str = f"Произошла неизвестная науке ошибка {err}"
    else:
        message_text = f'Заявка "{title}" принята. Номер заявки - {ticket_id}'
    logging.info(message_text)
    await bot.send_message(user_id, message_text, reply_markup=select_command)
    ddd = await bot.answer_callback_query(callback_id)
    logging.info("callback done %s", ddd)


async def refuse_solution(
    callback_query: types.CallbackQuery,
    state: FSMContext,
) -> None:
    """ Start a process of refusal """
    callback_id: str = callback_query.id
    user_id: int = callback_query.from_user.id
    ticket_id: int = int(callback_query.data.split(":")[1])
    message_id: int = callback_query.message.message_id
    message_text: str = callback_query.message.text
    user_session = UserSession(user_id)
    await user_session.create(state)
    await user_session.add_field("ticket_id", str(ticket_id))

    await Form.to_explain_decline.set()
    await bot.send_message(
        user_id, "Заполните причину отклонения", reply_markup=select_cancel_create
    )
    ddd = await bot.answer_callback_query(callback_id)
    logging.info("callback done %s", ddd)
    await bot.edit_message_text(
        message_text,
        chat_id=user_id,
        message_id=message_id,
        reply_markup=None,
    )


async def process_to_explain_decline(
    user_id: int, text: str, state: FSMContext
) -> None:
    """ Process declitation explain and decline ticket """
    user_session = UserSession(user_id)
    await user_session.create(state)
    ticket_id: int = int(await user_session.pop_field(key="ticket_id"))
    result = user_session.refuse_ticket_solition(ticket_id, text)
    logging.info("user_session.refuse_ticket_solition = %s", result)
    await Form.logged_in.set()
    await bot.send_message(user_id, "Принято", reply_markup=select_command)


async def refuse_solution_wrong_state(callback_id: str) -> None:
    """ Do not start a process of refusal """
    ddd = await bot.answer_callback_query(
        callback_id,
        text="Завершите текущие дела, и нажмите кнопку еще раз",
        show_alert=True,
    )
    logging.info("callback done %s", ddd)


# UNKNOWN ==================================================================
async def text_message(user_id: int, state: FSMContext) -> None:
    """React on something it cannot understand

    Args:
        user_id (int): telegram user id that issued command
    """
    if state is None:
        reply_markup = no_keyboard
    else:
        reply_markup = select_command
    # await bot.send_message(user_id, get_quote(), reply_markup=no_keyboard)
    await bot.send_message(
        user_id,
        "К сожалению, наш робот Вас не понял. Попробуйте ещё раз или введите /help",
        reply_markup=reply_markup,
    )
