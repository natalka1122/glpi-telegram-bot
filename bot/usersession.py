"""Module for UserSession class"""
import logging
from typing import Any, Dict, List, Optional, Union
import html2text
import html2markdown

from aiogram.dispatcher.storage import FSMContext

import config
import bot.glpi_api as glpi_api
from bot.db.dbhelper import DBHelper

LOGIN = "login"
PASSWORD = "password"
LOGGED_IN = "logged_in"
GLPI_ID = "glpi_id"
TICKET = "ticket"
USER = "user"
SOLUTION = "itilsolution"
TICKET_ID = "2"
REQUEST_USER_ID = "4"
TICKET_STATUS = "12"
TICKET_NAME = "1"
TICKET_LAST_UPDATE = "19"
CLOSED_TICKED_STATUS = "6"
ASSIGNED_TO = "5"


class StupidError(Exception):
    """Exception raised by this module."""


class UserSession:
    """General class for user"""

    # TODO Write a proper docstring
    # TODO Add support for password change of password
    # TODO Catch errors

    URL = config.GLPI_BASE_URL

    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
        self.state: Optional[FSMContext] = None
        self.login: Optional[str] = None
        self.password: Optional[str] = None
        self.glpi_id: Optional[int] = None
        self.is_logged_in: bool = False

    async def create(
        self,
        state: Optional[FSMContext] = None,
        dbhelper: Optional[DBHelper] = None,
        login: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Async replacement for __init__"""
        if state is None:
            if dbhelper is None:
                raise StupidError(
                    "UserSession.create: state == None and dbhelper == None"
                )
            state = FSMContext(storage=dbhelper, user=self.user_id, chat=self.user_id)
        elif dbhelper is not None:
            raise StupidError(
                f"UserSession.create: state == {state} and dbhelper == {dbhelper}"
            )

        self.state = state
        data: Dict = await self.state.get_data()
        if password is None:
            pwd_hidden: str = str(None)
        else:
            pwd_hidden = "_" + "*" * len(password) + "_"
        if PASSWORD in data:
            data_hidden = {}
            for key in data:
                if key == PASSWORD:
                    value = "_" + "*" * len(data[PASSWORD]) + "_"
                else:
                    value = data[key]
                data_hidden[key] = value
        else:
            data_hidden = data

        logging.info(
            "UserSesion create. user_id: %d login: %s, password: %s, data: %s",
            self.user_id,
            login,
            pwd_hidden,
            data_hidden,
        )

        if data is None and login is None and password is None:
            raise StupidError("Usage error -- No info to create a UserSession")

        if data is None:
            if login is not None and password is not None:
                self.login = login
                self.password = password
                self.glpi_id = self.check_cred()
                self.state.set_data(
                    data={
                        LOGIN: self.login,
                        PASSWORD: self.password,
                        GLPI_ID: self.glpi_id,
                        LOGGED_IN: True,
                    }
                )
                return
            if login is not None:
                self.state.set_data(data={LOGIN: login})
                return
            if password is not None:
                raise StupidError(
                    f"Usage error -- login is None, password = {pwd_hidden}"
                )

        flag_data_changed: bool = False
        if login is not None:
            data[LOGIN] = login
            flag_data_changed = True
        if password is not None:
            data[PASSWORD] = password
            flag_data_changed = True

        if LOGIN in data:
            self.login = data[LOGIN]
        if PASSWORD in data:
            self.password = data[PASSWORD]
        if GLPI_ID in data:
            self.glpi_id = data[GLPI_ID]
        if (
            (login is not None or password is not None)
            and self.login is not None
            and self.password is not None
        ):
            try:
                data[GLPI_ID] = self.check_cred()
            except glpi_api.GLPIError:
                data[LOGGED_IN] = False
                try:
                    del data[GLPI_ID]
                except KeyError:
                    pass
                if flag_data_changed:
                    await state.set_data(data=data)
                raise
            else:
                data[LOGGED_IN] = True
            flag_data_changed = True
        # if LOGGED_IN in data:
        # logging.info("data = %s", data)
        self.is_logged_in = data.get(LOGGED_IN, False)
        self.glpi_id = data.get(GLPI_ID, None)
        # if GLPI_ID in data:
        #     self.glpi_id = data[GLPI_ID]
        if flag_data_changed:
            await state.set_data(data=data)

    def __repr__(self) -> str:
        return (
            "UserSession() ="
            + f" user_id =_{self.user_id}_"
            + f" login =_{self.login}_"
            + f" password =_{self.password}_"
            + f" is_logged_in = _{self.is_logged_in}_"
            + f" state = _{self.state}_"
        )

    async def destroy(self, state: FSMContext = None) -> None:
        """Destroy all user data and state

        Args:
            state (FSMContext): state to destroy
        """
        if self.state is None and state is None:
            raise StupidError("No state provided")
        if self.state is not None and state is not None and self.state != state:
            raise StupidError("Two confusing states provided")
        if state is not None:
            await state.reset_state()
        elif self.state is not None:
            await self.state.reset_state()
        else:
            raise StupidError(f"Program error: self.state={self.state} state={state}")

    def check_cred(self) -> Optional[int]:
        """
        Raise error if no login with provided credentials
        """
        if self.login is None or self.password is None:
            raise glpi_api.GLPIError
        with glpi_api.GLPI(
            url=self.URL,
            auth=(self.login, self.password),
            apptoken=config.GLPI_APP_API_KEY,
        ) as glpi:
            result: Dict[str, Any] = glpi.get_full_session()
            # logging.info("get_full_session = %s", result)
            return result.get("glpiID", None)
        raise glpi_api.GLPIError

    async def add_field(self, key: str, data: str) -> None:
        """Add datafield to user_id in database

        Args:
            key (str): key to add
            data (str): value to add
        """
        if self.state is None:
            raise StupidError("self.state = None")
        await self.state.update_data(data={key: data})

    async def pop_field(self, key: str, default: str = "") -> str:
        """Delete field from data and return it's value

        Args:
            key (str): normally user_id
            default (str, optional): default value if the key does not exist. Defaults to "".

        Returns:
            str: field value
        """

        if self.state is None:
            raise StupidError("self.state = None")
        data = await self.state.get_data()
        if key not in data:
            logging.warning("pop_field: there is no {key} in {data}")
            return default
        result = data[key]
        del data[key]
        await self.state.set_data(data)
        return result

    def get_all_my_tickets(self, open_only: bool, full_info: bool) -> Dict[int, Dict]:
        """
        Return all tickets
        """
        if self.login is None or self.password is None or not self.is_logged_in:
            raise glpi_api.GLPIError
        # TODO error catch
        criteria = [
            {
                "field": REQUEST_USER_ID,
                "searchtype": "equals",
                "value": str(self.glpi_id),
            }
        ]
        forcedisplay = [TICKET_NAME, TICKET_STATUS, TICKET_LAST_UPDATE, ASSIGNED_TO]
        with glpi_api.GLPI(
            url=self.URL,
            auth=(self.login, self.password),
            apptoken=config.GLPI_APP_API_KEY,
        ) as glpi:
            glpi_tickets: List[Dict[str, Union[str, int, list, None]]] = glpi.search(
                TICKET, criteria=criteria, forcedisplay=forcedisplay, sort=TICKET_ID
            )
            logging.info("self.login = %s", self.login)
            logging.info("criteria = %s", criteria)
            logging.info("forcedisplay = %s", forcedisplay)
            logging.info("my_ticket_id = %s", glpi_tickets)
            if open_only:
                glpi_tickets = list(
                    filter(lambda x: x[TICKET_STATUS] != 6, glpi_tickets)
                )
            result: Dict[int, Dict] = {}
            if full_info:
                for elem in glpi_tickets:
                    ticket_id: int = int(elem[TICKET_ID])
                    result[ticket_id] = glpi.get_item(
                        TICKET, item_id=ticket_id, get_hateoas=False
                    )
                    # assigned_user_id: List[int] = []
                    # if isinstance(elem[ASSIGNED_TO], int):
                    #     assigned_user_id = [elem[ASSIGNED_TO]]
                    # elif isinstance(elem[ASSIGNED_TO], list):
                    #     assigned_user_id = elem[ASSIGNED_TO]
                    # elif elem[ASSIGNED_TO] is not None:
                    #     raise StupidError(
                    #         "elem[ASSIGNED_TO] = "
                    #         + str(elem[ASSIGNED_TO])
                    #         + " type = "
                    #         + str(type(elem[ASSIGNED_TO]))
                    #     )
                    # assigned_user: List[str] = []
                    # for user_id in assigned_user_id:
                    #     assigned_user.append(
                    #         glpi.get_item(USER, item_id=int(user_id), get_hateoas=False)
                    #     )
                    # result[ticket_id]["assigned_to"] = assigned_user
            else:
                for elem in glpi_tickets:
                    result[int(elem[TICKET_ID])] = {
                        "status": int(elem[TICKET_STATUS]),
                        "name": elem[TICKET_NAME],
                        "date_mod": elem[TICKET_LAST_UPDATE],
                    }
            return result
        raise glpi_api.GLPIError

    def get_one_ticket(self, ticket_id: int) -> Dict:
        """
        Return one ticket with ticket_id
        """
        if self.login is None or self.password is None or not self.is_logged_in:
            raise glpi_api.GLPIError
        with glpi_api.GLPI(
            url=self.URL,
            auth=(self.login, self.password),
            apptoken=config.GLPI_APP_API_KEY,
        ) as glpi:
            result = glpi.get_item(TICKET, item_id=ticket_id, get_hateoas=False)
            if "content" in result:
                result["content"] = html2markdown.convert(
                    html2text.html2text(str(result["content"]))
                )
            return result
        raise glpi_api.GLPIError

    def get_last_solution(self, ticket_id: int) -> str:
        """
        Return last proposed solution for ticket with ticket_id
        """
        if self.login is None or self.password is None or not self.is_logged_in:
            raise glpi_api.GLPIError
        with glpi_api.GLPI(
            url=self.URL,
            auth=(self.login, self.password),
            apptoken=config.GLPI_APP_API_KEY,
        ) as glpi:
            solution: Dict = glpi.get_sub_items(
                TICKET, ticket_id, SOLUTION, get_hateoas=False
            )
            logging.info("solution = %s", solution)
            if len(solution) < 1:
                return ""
            return html2markdown.convert(
                html2text.html2text(str(solution[-1].get("content")))
            )
        raise glpi_api.GLPIError

    def create_ticket(self, title: str, description: str, urgency: int) -> int:
        """
        Create one ticket with specified title
        """
        if self.login is None or self.password is None or not self.is_logged_in:
            raise glpi_api.GLPIError
        try:
            with glpi_api.GLPI(
                url=self.URL,
                auth=(self.login, self.password),
                apptoken=config.GLPI_APP_API_KEY,
            ) as glpi:
                result = glpi.add(
                    TICKET,
                    {"name": title, "content": description, "urgency": urgency},
                )
                if isinstance(result, list) and len(result) == 1 and "id" in result[0]:
                    return result[0]["id"]
                raise StupidError("Failed to add ticket: {}".format(result))
        except glpi_api.GLPIError as err:
            raise StupidError("Failed to add ticket: {}".format(err)) from err
        raise glpi_api.GLPIError
        # [{'id': 1309, 'message': 'Объект успешно добавлен: dds'}]

    def approve_ticket_solution(self, ticket_id: int) -> None:
        """ Close ticket """
        if self.login is None or self.password is None or not self.is_logged_in:
            raise glpi_api.GLPIError
        with glpi_api.GLPI(
            url=self.URL,
            auth=(self.login, self.password),
            apptoken=config.GLPI_APP_API_KEY,
        ) as glpi:
            # result = glpi.update(
            #     "ticket", {"id": ticket_id, "status": CLOSED_TICKED_STATUS}
            # )
            result = glpi.add(
                "itilfollowup",
                {
                    "itemtype": TICKET,
                    "items_id": ticket_id,
                    "content": "",
                    "is_private": 0,
                    "add_close": 1,
                },
            )
            logging.info("result = %s", result)

    def refuse_ticket_solition(self, ticket_id: int, text: str) -> List[Dict]:
        """ Add followup and reopen ticket """
        if self.login is None or self.password is None or not self.is_logged_in:
            raise glpi_api.GLPIError
        with glpi_api.GLPI(
            url=self.URL,
            auth=(self.login, self.password),
            apptoken=config.GLPI_APP_API_KEY,
        ) as glpi:
            return glpi.add(
                "itilfollowup",
                {
                    "itemtype": TICKET,
                    "items_id": ticket_id,
                    "content": text,
                    "is_private": 0,
                    "add_reopen": 1,
                },
            )
        raise glpi_api.GLPIError
