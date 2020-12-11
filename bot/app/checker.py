"""Thread function for regular check of glpi server
"""
import typing
import logging
import asyncio
import aioschedule
import config
from bot.app.core import bot
from bot.db.dbhelper import DBHelper
from bot.usersession import UserSession, StupidError

STATUS ="status"


def check_diff(
    old_tickets_list: typing.List[typing.Dict],
    new_tickets_list: typing.List[typing.Dict],
):
    """ Read old data, compare it with the new data, rewrite new data, return diff """
    logging.info("len(old_tickets_list) = %s", len(old_tickets_list))
    logging.info("len(new_tickets_list) = %s", len(new_tickets_list))
    old_ticket_dict: typing.Dict[
        int, typing.Dict[str, typing.Union[None, int, str]]
    ] = {ticket["id"]: ticket for ticket in old_tickets_list}
    new_ticket_dict: typing.Dict[
        int, typing.Dict[str, typing.Union[None, int, str]]
    ] = {ticket["id"]: ticket for ticket in new_tickets_list}

    messages: typing.Dict[int, str] = dict()
    have_changes: bool = False
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
                if old_ticket_dict[ticket_id].get(elem,None) != new_ticket_dict[ticket_id].get(elem,None):
                    have_changes = True
            old_status = old_ticket_dict[ticket_id].get(STATUS,None)
            new_status = new_ticket_dict[ticket_id].get(STATUS,None)
            if old_status != new_status:
                messages[ticket_id] = f"Status: old = {old_status} new = {new_status}"
        elif ticket_id in old_ticket_dict and ticket_id not in new_ticket_dict:
            logging.info("Deleted (?) ticket: %s", new_ticket_dict[ticket_id])
            # TODO Think about it
            messages[ticket_id] = "DELETE (?)"
            have_changes = True
        elif ticket_id not in old_ticket_dict and ticket_id in new_ticket_dict:
            logging.info("I've got %s", new_ticket_dict[ticket_id])
            # TODO Think about it
            messages[ticket_id] = "NEW"
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
    return messages, have_changes


# def write_diff(dbhelper: DBHelper, replace_ticket_dict, delete_ticket_list):
#     logging.info("replace_ticket_dict = %s", replace_ticket_dict)
#     logging.info("delete_ticket_list = %s", delete_ticket_list)
#     # dbhelper.update_tickets(
#     #     replace_ticket_dict=replace_ticket_dict, delete_ticket_id=delete_ticket_list
#     # )


async def run_check(dbhelper: DBHelper):
    """Check for every user if it has updates"""
    # TODO add error catch
    for user_id in dbhelper.all_user():
        logging.info("checker.run_check: user_id = %s", user_id)
        user_session: UserSession = UserSession(user_id)
        await user_session.create(dbhelper=dbhelper)
        if not user_session.is_logged_in or user_session.glpi_id is None:
            # TODO notify user if he is suddenly unlogged (due password change or else)
            continue
        old_tickets = dbhelper.all_tickets_glpi(user_session.glpi_id)
        new_tickets = user_session.get_all_tickets()
        logging.debug(
            "checker.run_check: old_tickets = %d %s", len(old_tickets), old_tickets
        )
        logging.debug(
            "checker.run_check: new_tickets = %d %s", len(new_tickets), new_tickets
        )
        messages, have_changes = check_diff(old_tickets, new_tickets)
        if have_changes:
            dbhelper.write_tickets_glpi(glpi_id=user_session.glpi_id, data=new_tickets)
            # write_diff(
            #     glpi_id=user_session.glpi_id, tickets=new_tickets, dbhelper=dbhelper
            # )

        logging.info("checker.run_check: messages = %s", messages)
        for ticket_id in messages:
            logging.info(
                "checker.run_check: user_id = %s, ticket_id = %s message = %s",
                user_id,
                ticket_id,
                messages[ticket_id],
            )
            await bot.send_message(
                user_id, f"ticket_id = {ticket_id} message = {messages[ticket_id]}"
            )


async def scheduler(dbhelper: DBHelper):
    """ Main scheduler for regilar ticket check """
    aioschedule.every(config.CHECK_PERIOD).seconds.do(run_check, dbhelper=dbhelper)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
