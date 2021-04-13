"""Thread function for regular check of glpi server
"""
import typing
import logging
import asyncio
import aiogram
from aiogram.dispatcher import FSMContext
import aioschedule
from config import CHECK_PERIOD, GLPI_TICKET_URL
from bot.app.core import bot
import bot.app.keyboard as keyboard
from bot.db.dbhelper import DBHelper
from bot.usersession import UserSession, StupidError
from bot.glpi_api import GLPIError
import bot.app.generic.generic as generic

STATUS = "status"


def check_diff(
    old_ticket_dict: typing.Dict[int, typing.Dict],
    new_ticket_dict: typing.Dict[int, typing.Dict],
    user_session: UserSession,
) -> typing.Tuple[typing.Tuple[typing.Dict, typing.Dict, typing.Dict], bool]:
    """ Read old data, compare it with the new data, rewrite new data, return diff """
    logging.info("len(old_ticket_dict) = %s", len(old_ticket_dict))
    logging.info("len(new_ticket_dict) = %s", len(new_ticket_dict))
    logging.info("old_ticket_dict = %s", old_ticket_dict)
    logging.info("new_ticket_dict = %s", new_ticket_dict)
    # old_ticket_dict: typing.Dict[
    #     int, typing.Dict[str, typing.Union[None, int, str]]
    # ] = {ticket["id"]: ticket for ticket in old_tickets_list}
    # new_ticket_dict: typing.Dict[
    #     int, typing.Dict[str, typing.Union[None, int, str]]
    # ] = {ticket["id"]: ticket for ticket in new_tickets_list}

    messages: typing.Dict[int, str] = dict()
    have_changes: bool = False
    proposed_solutions = dict()
    closed_tickets = dict()
    for ticket_id in old_ticket_dict.keys() | new_ticket_dict.keys():
        logging.info("got ticket_id %s", ticket_id)
        logging.info(
            "in old_ticket_dict: %s, in new_ticket_dict: %s",
            ticket_id in old_ticket_dict,
            ticket_id in new_ticket_dict,
        )
        if ticket_id in old_ticket_dict and ticket_id in new_ticket_dict:
            for elem in old_ticket_dict[ticket_id]:
                # logging.info(f"old_ticket_dict[ticket_id] = {old_ticket_dict[ticket_id]}")
                # logging.info(f"type = {type(old_ticket_dict[ticket_id])} elem = {type(elem)} {elem}")
                if old_ticket_dict[ticket_id].get(elem, None) != new_ticket_dict[
                    ticket_id
                ].get(elem, None):
                    have_changes = True
            old_status = old_ticket_dict[ticket_id].get(STATUS, None)
            new_status = new_ticket_dict[ticket_id].get(STATUS, None)
            if old_status != new_status:
                name: str = (
                    '"' +
                    str(new_ticket_dict[ticket_id].get("name", None)) + '"'
                )
                date_mod: str = str(
                    new_ticket_dict[ticket_id].get("date_mod", None))
                # messages[ticket_id] = f"Status: old = {old_status} new = {new_status}"
                if new_status == 1:  # Новый
                    messages[ticket_id] = (
                        f"Ваша заявка с номером <a href=\"{GLPI_TICKET_URL}{ticket_id}\">{ticket_id} {name}</a> пересоздана."
                        + f" Дата и время назначения: {date_mod}"
                    )
                elif new_status == 2:  # В работе (назначена)
                    messages[ticket_id] = (
                        f"Ваша заявка с номером <a href=\"{GLPI_TICKET_URL}{ticket_id}\">{ticket_id} {name}</a> назначена."
                        + f" Дата и время назначения: {date_mod}"
                    )
                elif new_status == 3:  # В работе (запланирована)
                    messages[ticket_id] = (
                        f"Ваша заявка с номером <a href=\"{GLPI_TICKET_URL}{ticket_id}\">{ticket_id} {name}</a> запланирована."
                        + f" Дата и время изменения: {date_mod}"
                    )
                elif new_status == 4:  # Ожидает ответа от заявителя
                    messages[ticket_id] = (
                        f"Ваша заявка с номером <a href=\"{GLPI_TICKET_URL}{ticket_id}\">{ticket_id} {name}</a>"
                        + f" ожидает ответа от заявителя. Дата и время изменения: {date_mod}"
                    )
                elif new_status == 5:  # Решена
                    solution: str = user_session.get_last_solution(ticket_id)
                    messages[ticket_id] = (
                        f"По Вашей заявке с номером <a href=\"{GLPI_TICKET_URL}{ticket_id}\">{ticket_id} {name}</a>"
                        + f" предложено решение: {solution}.\nДата и время изменения: {date_mod}"
                    )
                    proposed_solutions[ticket_id] = messages[ticket_id]
                    # TODO Add buttons
                elif new_status == 6:  # Закрыто
                    messages[ticket_id] = ""
                    closed_tickets[ticket_id] = messages[ticket_id]
                    # TODO Add button
                else:
                    messages[
                        ticket_id
                    ] = f"Status: old = {old_status} new = {new_status}"
                    logging.error(
                        "UNKNOWN STATUS: old = %s new = %s", old_status, new_status
                    )
                    logging.error("old_ticket = %s",
                                  old_ticket_dict[ticket_id])
                    logging.error("new_ticket = %s",
                                  new_ticket_dict[ticket_id])
        elif ticket_id in old_ticket_dict and ticket_id not in new_ticket_dict:
            logging.info("Deleted ticket: %s", old_ticket_dict[ticket_id])
            # TODO Think about it
            messages[
                ticket_id
            ] = f"Ваша заявка с номером {ticket_id} \"{old_ticket_dict[ticket_id].get('name',None)}\" удалена."
            have_changes = True
        elif ticket_id not in old_ticket_dict and ticket_id in new_ticket_dict:
            logging.info("New ticket %s", new_ticket_dict[ticket_id])
            # TODO Think about it
            # messages[ticket_id] = "NEW"
            have_changes = True
        elif ticket_id not in old_ticket_dict and ticket_id in new_ticket_dict:
            logging.error(
                "Impossible: ticket_id not in old_ticket_dict and ticket_id in new_ticket_dict"
            )
            logging.error("ticket_id = %s", ticket_id)
            logging.error("old_ticket_dict = %s", old_ticket_dict)
            logging.error("new_ticket_dict = %s", new_ticket_dict)
            raise StupidError("Never ever can I get here")
        else:
            logging.error("Impossible: ELSE")
            logging.error("ticket_id = %s", ticket_id)
            logging.error("old_ticket_dict = %s", old_ticket_dict)
            logging.error("new_ticket_dict = %s", new_ticket_dict)
            raise StupidError("Never ever can I get here")

        continue
    logging.info("messages = %s", messages)
    return (messages, proposed_solutions, closed_tickets), have_changes


# def write_diff(dbhelper: DBHelper, replace_ticket_dict, delete_ticket_list):
#     logging.info("replace_ticket_dict = %s", replace_ticket_dict)
#     logging.info("delete_ticket_list = %s", delete_ticket_list)
#     # dbhelper.update_tickets(
#     #     replace_ticket_dict=replace_ticket_dict, delete_ticket_id=delete_ticket_list
#     # )


async def process_messages(
    user_id: int,
    messages: typing.Dict,
    proposed_solutions: typing.Dict,
    closed_tickets: typing.Dict,
) -> None:
    """Sends messages about changed tickets to user

    Args:
        user_id ([type]): [description]
        messages ([type]): [description]
        proposed_solutions ([type]): [description]
        closed_tickets ([type]): [description]
    """
    # TODO Write proper docstring
    for ticket_id in proposed_solutions:
        logging.info(
            "proposed_solution: user_id = %s, ticket_id = %s message = %s",
            user_id,
            ticket_id,
            messages[ticket_id],
        )
        message: aiogram.types.Message = await bot.send_message(
            user_id,
            messages[ticket_id],
            reply_markup=keyboard.select_approve_refuse(ticket_id),
        )
        logging.info("message = %s %s", message.message_id, message)
        del messages[ticket_id]

    for ticket_id in closed_tickets:
        logging.info(
            "closed_tickets: user_id = %s, ticket_id = %s message = %s",
            user_id,
            ticket_id,
            messages[ticket_id],
        )
        # await bot.send_message(
        #     user_id,
        #     f"closed_ticket: {messages[ticket_id]}",
        #     reply_markup=keyboard.select_repeat_ticket(ticket_id),
        # )
        del messages[ticket_id]

    for ticket_id in messages:
        logging.info(
            "user_id = %s, ticket_id = %s message = %s",
            user_id,
            ticket_id,
            messages[ticket_id],
        )
        await bot.send_message(user_id, f"{messages[ticket_id]}")


async def run_check(dbhelper: DBHelper) -> None:
    """Check for every user if it has updates"""
    # TODO add error catch
    for user_id in dbhelper.all_user():
        logging.info("checker.run_check: user_id = %s", user_id)
        user_session: UserSession = UserSession(user_id)
        await user_session.create(dbhelper=dbhelper)
        if not user_session.is_logged_in or user_session.glpi_id is None:
            # TODO notify user if he is suddenly unlogged (due password change or else)
            continue
        old_tickets: typing.Dict[int, typing.Dict] = dbhelper.all_tickets_glpi(
            user_session.glpi_id
        )
        try:
            new_tickets: typing.Dict[int, typing.Dict] = user_session.get_all_my_tickets(
                open_only=False, full_info=False
            )
        except GLPIError as err:
            # logging.info(err.__dict__)
            error_text = str(err)
            logging.info("error_text = %s", error_text)
            if "Incorrect username or password" in error_text:
                await generic.logout(user_id, FSMContext(
                    storage=dbhelper, chat=user_id, user=user_id))
                continue
            else:
                raise

        logging.debug(
            "checker.run_check: old_tickets = %d %s", len(
                old_tickets), old_tickets
        )
        logging.debug(
            "checker.run_check: new_tickets = %d %s", len(
                new_tickets), new_tickets
        )
        messages, have_changes = check_diff(
            old_tickets, new_tickets, user_session=user_session
        )
        if have_changes:
            dbhelper.write_tickets_glpi(
                glpi_id=user_session.glpi_id, data=new_tickets)
            logging.info("checker.run_check: messages = %s", messages)
            await process_messages(user_id, *messages)

        # for ticket_id in messages:
        #     logging.info(
        #         "checker.run_check: user_id = %s, ticket_id = %s message = %s",
        #         user_id,
        #         ticket_id,
        #         messages[ticket_id],
        #     )
        #     await bot.send_message(user_id, f"{messages[ticket_id]}")


async def scheduler(dbhelper: DBHelper) -> None:
    """ Main scheduler for regilar ticket check """
    aioschedule.every(CHECK_PERIOD).seconds.do(run_check, dbhelper=dbhelper)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
