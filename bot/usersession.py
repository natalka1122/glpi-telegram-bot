"""Module for UserSession class"""
import config
import bot.glpi_api as glpi_api
from bot.app import core


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

    # TODO Add support for password change of password

    URL = config.GLPI_BASE_URL

    def __init__(self, user_id, login=None, password=None):
        data = core.db_connect.get_data(user_id)

        if data is None and (login is None or password is None):
            raise StupidError

        self.user_id = user_id
        if data is None:
            self.login = login
            self.password = password
            self.check_cred()
            core.db_connect.add_data(
                user_id, {"login": self.login, "password": self.password}
            )
            return

        self.login = data["login"]
        self.password = data["password"]

    def check_cred(self):
        """
        Raise error if no login with provided credentials
        """
        with glpi_api.connect(
            url=self.URL, auth=(self.login, self.password), apptoken=""
        ):
            pass

    def get_all_tickets(self):
        """
        Return all tickets
        """
        with glpi_api.connect(
            url=self.URL, auth=(self.login, self.password), apptoken=""
        ) as glpi:
            return glpi.get_all_items("ticket")

    def create_ticket(self, title):
        """
        Create one ticket with specified title
        """
        with glpi_api.connect(
            url=self.URL, auth=(self.login, self.password), apptoken=""
        ) as glpi:
            result = glpi.add("ticket", {"name": title})
        # [{'id': 1309, 'message': 'Объект успешно добавлен: dds'}]
        if isinstance(result, list) and len(result) == 1 and "id" in result[0]:
            return result[0]["id"]

        raise StupidError("Failed to add ticket: {}".format(result))

    def get_one_ticket(self, ticket_id):
        """
        Return one ticket with ticket_id
        """
        with glpi_api.connect(
            url=self.URL, auth=(self.login, self.password), apptoken=""
        ) as glpi:
            return glpi.get_item("ticket", ticket_id)
