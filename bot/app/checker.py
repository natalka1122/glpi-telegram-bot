"""Thread function for regular check of glpi server
"""
import typing
import logging
import asyncio
import aioschedule
import config
import bot.glpi_api as glpi_api
from bot.db.dbhelper import DBHelper


def check_and_save_diff(dbhelper: DBHelper, new_tickets: typing.List[typing.Dict]):
    """ Read old data, compare it with the new data, rewrite new data, return diff """
    logging.info(dbhelper.export())
    # for ticket in dbhelper.get_all_tickets():

    raise NotImplementedError("check_and_save_diff")


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
            all_tickets: typing.List[typing.Dict] = glpi.get_all_items("ticket")
    else:
        raise NotImplementedError(f"config.GLPI_USER_ADMIN = {config.GLPI_USE_ADMIN}")
    logging.info("%s", all_tickets)
    check_and_save_diff(dbhelper, all_tickets)
    # tasks = []
    # for user in affected_users:
    #     tasks.append(notify_user(___))


async def scheduler(dbhelper: DBHelper):
    """ Main scheduler for regilar ticket check """
    aioschedule.every(config.CHECK_PERIOD).seconds.do(run_check, dbhelper=dbhelper)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
