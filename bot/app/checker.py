"""Thread function for regular check of glpi server
"""
import typing
import logging
import functools
import traceback
import asyncio
import aioschedule
import config
import bot.glpi_api as glpi_api
from bot.db.dbhelper import DBHelper


def check_and_save_diff(dbhelper: DBHelper, new_tickets_list: typing.List[typing.Dict]):
    """ Read old data, compare it with the new data, rewrite new data, return diff """
    new_ticket_dict: typing.Dict[
        int, typing.Dict[str, typing.Union[None, int, str]]
    ] = {ticket["id"]: ticket for ticket in new_tickets_list}
    delete_ticket_list: typing.List[int] = []
    messages: typing.Dict[int, typing.Dict[str, typing.Union[None, int, str]]] = dict()
    for old_ticket in dbhelper.all_tickets_generator():
        logging.info("got ticket %s", old_ticket)
        ticket_id: int = old_ticket["id"]
        if ticket_id in new_ticket_dict:
            new_ticket: typing.Dict[
                str, typing.Union[None, int, str]
            ] = new_ticket_dict[ticket_id]
            user_id: int = new_ticket["users_id_recipient"]
            there_is_no_change: bool = True
            for elem in new_ticket_dict[ticket_id].keys() | old_ticket.keys():
                old_value: typing.Union[None, int, str] = old_ticket.get(elem, None)
                new_value: typing.Union[None, int, str] = new_ticket.get(elem, None)
                if old_value != new_value:
                    logging.info(
                        "GOT CHANGE ticket_id = %s, elem = %s old_value(%s) = %s new_value(%s) = %s",
                        ticket_id,
                        elem,
                        type(old_value),
                        old_value,
                        type(new_value),
                        new_value,
                    )
                    there_is_no_change = False
                    if elem == "status":
                        if new_value == 2:
                            logging.info(
                                "NOTIFY USER"
                                " При переходе заявки в статус «В работе(назначена)» от бота поступает сообщение"
                            )
                        elif new_value == 3:
                            logging.info(
                                "NOTIFY USER"
                                " При переходе заявки в статус «processing(Planned)» от бота поступает сообщение"
                            )
                        elif new_value == 4:
                            logging.info(
                                "NOTIFY USER"
                                " При переходе заявки в статус «Pending» от бота поступает сообщение"
                            )
                        elif new_value == 5:
                            logging.info(
                                "NOTIFY USER"
                                " При переходе заявки в статус «Solved» от бота поступает сообщение"
                            )
                        elif new_value == 6:
                            logging.info(
                                "NOTIFY USER"
                                " При переходе заявки в статус «Closed» от бота поступает сообщение"
                            )
                        else:
                            logging.info(
                                "NOTIFY USER Старый статус %s Новый статус %s",
                                old_value,
                                new_value,
                            )
                        messages[user_id] = {"status": new_value}
            if there_is_no_change:
                logging.info("ticket_id = %s not change", ticket_id)
                del new_ticket_dict[ticket_id]
        else:  # ticket_id not in new_ticket_dict:
            delete_ticket_list.append(ticket_id)
    dbhelper.update_tickets(
        add_ticket_dict=new_ticket_dict, delete_ticket_id=delete_ticket_list
    )
    return messages


async def run_check(dbhelper: DBHelper):
    """Check for every user if it has updates"""
    if config.GLPI_USE_ADMIN:
        if len(config.GLPI_ADMIN_API_KEY) == 0:
            cred: typing.Union[typing.Tuple[str, str], str] = (
                config.GLPI_ADMIN_LOGIN,
                config.GLPI_ADMIN_PASSWORD,
            )
        else:
            cred = config.GLPI_ADMIN_API_KEY
        with glpi_api.connect(
            url=config.GLPI_BASE_URL, auth=cred, apptoken=config.GLPI_APP_API_KEY
        ) as glpi:
            all_tickets: typing.List[typing.Dict] = glpi.get_all_items(
                "ticket", get_hateoas=False
            )
    else:
        raise NotImplementedError(f"config.GLPI_USE_ADMIN = {config.GLPI_USE_ADMIN}")
    # for ticket in all_tickets:
    #     logging.info("==*==" * 10)
    #     for elem in ticket:
    #         logging.info("%s: %s", elem, ticket[elem])
    messages: typing.Dict[
        int, typing.Dict[str, typing.Union[None, int, str]]
    ] = check_and_save_diff(dbhelper, all_tickets)
    # tasks = []
    # for user in affected_users:
    #     tasks.append(notify_user(___))


async def scheduler(dbhelper: DBHelper):
    """ Main scheduler for regilar ticket check """
    aioschedule.every(config.CHECK_PERIOD).seconds.do(run_check, dbhelper=dbhelper)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
