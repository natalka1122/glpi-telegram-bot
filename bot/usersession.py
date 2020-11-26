"""Module for UserSession class"""
import logging
import typing

from aiogram.dispatcher.storage import FSMContext
import config
import bot.glpi_api as glpi_api

# from bot.app import core

LOGIN = "login"
PASSWORD = "password"
LOGGED_IN = "logged_in"
USER_ID = "id"

class StupidError(Exception):
    """Exception raised by this module."""


class UserSession:
    """General class for user
    There are two scenarios:
    1) UserSession(user_id, login, password)
        try to login, and if successful, then write data in database
    2) UserSession(user_id)
        read data from database.
    """

    # TODO Write a proper docstring
    # TODO Add support for password change of password
    # TODO Catch errors

    URL = config.GLPI_BASE_URL

    def __init__(self, user_id: int) -> None:
        self.user_id: int = user_id
        self.state: typing.Optional[FSMContext] = None
        self.login: typing.Optional[str] = None
        self.password: typing.Optional[str] = None
        self.is_logged_in: bool = False

    async def create(self, state: FSMContext, login=None, password=None):
        """Async replacement for __init__"""
        self.state = state
        data = await self.state.get_data()
        if password is None:
            pwd_hidden = str(None)
        else:
            pwd_hidden = "_" + "*" * len(password) + "_"
        logging.info(
            "UserSesion create. user_id: %d login: %s, password: %s, data: %s",
            self.user_id,
            login,
            pwd_hidden,
            data,
        )

        if data is None and login is None and password is None:
            raise StupidError("Usage error -- No info to create a UserSession")

        if data is None:
            if login is not None and password is not None:
                self.login = login
                self.password = password
                self.check_cred()
                self.state.set_data(
                    data={LOGIN: self.login, PASSWORD: self.password, LOGGED_IN: True}
                )
                return
            if login is not None:
                self.state.set_data(data={LOGIN: login})
                return
            if password is not None:
                logging.warning("Got password without login. Something is wrong")
                self.state.set_data(data={PASSWORD: password})
                return

        if login is not None:
            data[LOGIN] = login
        if password is not None:
            data[PASSWORD] = password

        if LOGIN in data:
            self.login = data[LOGIN]
        if PASSWORD in data:
            self.password = data[PASSWORD]
        if (
            (login is not None or password is not None)
            and self.login is not None
            and self.password is not None
        ):
            data[USER_ID] = self.check_cred()
            data[LOGGED_IN] = True
        if data.get(LOGGED_IN, False):
            self.is_logged_in = True
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

    async def destroy(self, state: FSMContext = None):
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

    def check_cred(self):
        """
        Raise error if no login with provided credentials
        """
        with glpi_api.connect(
            url=self.URL, auth=(self.login, self.password), apptoken=config.GLPI_APP_API_KEY
        ) as glpi:
            result = glpi.get_my_profiles()
        logging.info("get_my_profiles = %s",result)
        return result[0][USER_ID]


    async def add_field(self, key: str, data: str) -> None:
        """Add datafield to user_id in database

        Args:
            key (str): key to add
            data (str): value to add
        """
        await self.state.update_data(data={key: data})

    async def pop_field(self, key: str, default: str = "") -> str:
        """Delete field from data and return it's value

        Args:
            key (str): normally user_id
            default (str, optional): default value if the key does not exist. Defaults to "".

        Returns:
            str: field value
        """

        data = await self.state.get_data()
        if key not in data:
            logging.warning("pop_field: there is no {key} in {data}")
            return default
        result = data[key]
        del data[key]
        await self.state.set_data(data)
        return result

    def get_all_tickets(self) -> typing.List[typing.Dict]:
        """
        Return all tickets
        """
        with glpi_api.connect(
            url=self.URL, auth=(self.login, self.password), apptoken=config.GLPI_APP_API_KEY
        ) as glpi:
            return glpi.get_all_items("ticket")

    def create_ticket(self, title, description, urgency):
        """
        Create one ticket with specified title
        """
        with glpi_api.connect(
            url=self.URL, auth=(self.login, self.password), apptoken=config.GLPI_APP_API_KEY
        ) as glpi:
            result = glpi.add(
                "ticket",
                {"name": title, "content": description, "urgency": urgency},
            )
        # [{'id': 1309, 'message': 'Объект успешно добавлен: dds'}]
        if isinstance(result, list) and len(result) == 1 and "id" in result[0]:
            return result[0]["id"]

        raise StupidError("Failed to add ticket: {}".format(result))

    def get_one_ticket(self, ticket_id):
        """
        Return one ticket with ticket_id
        """
        with glpi_api.connect(
            url=self.URL, auth=(self.login, self.password), apptoken=config.GLPI_APP_API_KEY
        ) as glpi:
            return glpi.get_item("ticket", ticket_id)
