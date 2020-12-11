"""Manage comunication with vedis database
"""
import json
import logging
import typing
from aiogram.dispatcher.storage import BaseStorage
import vedis

STATE = "state"
DATA = "data"
BUCKET = "bucket"


def bytes_to_dict(source: bytes) -> typing.Dict:
    """Convert bytes into dict

    Args:
        source (bytes): Source string in bytes

    Returns:
        typing.Dict: Resulting dict
    """
    # logging.info("source = %s", source)
    # logging.info("result = %s", json.loads(source.decode("utf8")))
    return json.loads(source.decode("utf8"))


def dict_to_bytes(source: typing.Dict) -> bytes:
    """Converts dict into bytes

    Args:
        source (typing.Dict): Source dict

    Returns:
        bytes: Resulting string in bytes
    """
    # logging.info("source = %s", source)
    # logging.info("result = %s", json.dumps(source).encode("utf8"))
    return json.dumps(source).encode("utf8")


class DBHelper(BaseStorage):
    """Main class to communicate with vedis
    By default it write to memory, although it is highly recommended to use file instead.

    Problems:
    1) sometimes I have key as telegram user_id, and sometimes as glpi login
    2) there is no possibility to iterate over vedis keys
    3) one login can have more then one user_id
    """

    def __init__(self, filename: str = ":mem:"):
        logging.debug("DBHelper __init__")
        self._filename: str = filename
        self._database: vedis = vedis.Vedis(self._filename)
        self._userid: vedis.Hash = self._database.Hash("user_id")
        self._glpi_id: vedis.Hash = self._database.Hash("glpi")
        self._tickets: vedis.Hash = self._database.Hash("tickets")
        # export = self.export()
        # for key in export:
        #     logging.info("key = %s data = %s", key, export[key])

    async def close(self):
        logging.debug("DBHelper close")
        self._database.close()

    async def wait_closed(self):
        logging.debug("DBHelper wait_closed")

    def export(self) -> typing.Dict:
        """Exports database content

        Returns:
            typing.Dict: database content
        """
        logging.debug("DBHelper debug")
        result = {}
        with self._database.transaction():
            result["user_id"] = self._userid.to_dict()
            result["glpi_id"] = self._glpi_id.to_dict()
            result["ticket"] = self._tickets.to_dict()
        return result

    def all_tickets_glpi(self, glpi_id: int):
        """ Return all tickets for glpi user """
        with self._database.transaction():
            if self._tickets:
                if glpi_id in self._tickets:
                    return bytes_to_dict(self._tickets[glpi_id])
        return []

    def all_user(self):
        """ Return all user_id """
        logging.info("dbhelper.all_user")
        with self._database.transaction():
            logging.info(
                "self._userid = %s, self._userid.keys() = %s",
                self._userid,
                self._userid.keys(),
            )
            if self._userid.keys() is None:
                return []
            return map(bytes_to_dict, self._userid.keys())

    def write_tickets_glpi(self, glpi_id: int, data):
        """ Write tickets corresponding to specific glpi_id user """
        with self._database.transaction():
            self._tickets[glpi_id] = dict_to_bytes(data)

    # def update_tickets(
    #     self,
    #     replace_ticket_dict: typing.Dict = None,
    #     delete_ticket_id: typing.List[int] = None,
    # ):
    #     """ Add changed tickets, delete deleted tickets """
    #     if replace_ticket_dict is None:
    #         replace_ticket_dict = dict()
    #     if delete_ticket_id is None:
    #         delete_ticket_id = []
    #     if len(replace_ticket_dict) == 0 and len(delete_ticket_id) == 0:
    #         return

    #     logging.info(
    #         "update_tickets: replace_ticket_dict = %s %s delete_ticket_id = %s",
    #         len(replace_ticket_dict),
    #         replace_ticket_dict,
    #         delete_ticket_id,
    #     )
    #     with self._database.transaction():
    #         for ticket_id in replace_ticket_dict:
    #             self._tickets[ticket_id] = dict_to_bytes(replace_ticket_dict[ticket_id])
    #         for ticket_id in delete_ticket_id:
    #             del self._tickets[ticket_id]
    def _resolve_address(
        self, chat: typing.Union[str, int, None], user: typing.Union[str, int, None]
    ) -> str:
        """Fills data if the user is new

        Args:
            chat (int): chat_id for telegram
            user (int): user_id for telegram

        Raises:
            AttributeError: chat_id is not equal to user_id

        Returns:
            str: telegram user_id
        """
        chat, user = self.check_address(chat=chat, user=user)
        if chat != user:
            raise AttributeError(
                f"Program error: chat_id {chat} is not equal user_id {user}"
            )
        user_id = str(user)

        if user_id not in self._userid:
            self._userid[user_id] = dict_to_bytes({STATE: None, DATA: {}, BUCKET: {}})
        return user_id

    def _get_whole_data(
        self,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
    ) -> typing.Dict:
        """Return all known data for current telegram user

        Args:
            chat (typing.Union[str, int, None], optional): chat_id for telegram. Defaults to None.
            user (typing.Union[str, int, None], optional): user_id for telegram. Defaults to None.

        Returns:
            typing.Dict: [description]
        """
        user = self._resolve_address(chat=chat, user=user)
        with self._database.transaction():
            whole_data: typing.Dict = bytes_to_dict(self._userid[user])
        return whole_data

    def _set_whole_data(
        self,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        whole_data: typing.Dict = None,
    ) -> None:
        """Writes all known data for specific user to database

        Args:
            chat (typing.Union[str, int, None], optional): chat_id for telegram. Defaults to None.
            user (typing.Union[str, int, None], optional): user_id for telegram. Defaults to None.
            whole_data (typing.Dict, optional): data to store. Defaults to None.
        """
        if whole_data is None:
            whole_data = {}
        user = self._resolve_address(chat=chat, user=user)
        with self._database.transaction():
            self._userid[user] = dict_to_bytes(whole_data)

    async def get_state(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        default: typing.Optional[str] = None,
    ) -> typing.Optional[str]:
        logging.debug("DBHelper get_state")
        return self._get_whole_data(chat=chat, user=user).get(STATE, default)

    async def set_state(
        self,
        *,
        chat: typing.Union[str, int, None],
        user: typing.Union[str, int, None],
        state: typing.Optional[typing.AnyStr],
    ):
        logging.debug("DBHelper set_state %s", state)
        whole_data = self._get_whole_data(chat, user)
        whole_data[STATE] = state
        logging.info("DBHelper set_state writes %s", whole_data)
        self._set_whole_data(chat=chat, user=user, whole_data=whole_data)

    async def get_data(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        default: typing.Optional[typing.Dict] = None,
    ) -> typing.Dict:
        logging.debug("DBHelper get_data")
        return self._get_whole_data(chat, user).get(DATA, default)

    async def set_data(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        data: typing.Dict,
    ):
        logging.debug("DBHelper set_data")
        whole_data = self._get_whole_data(chat, user)
        whole_data[DATA] = data
        self._set_whole_data(chat=chat, user=user, whole_data=whole_data)

    async def update_data(
        self,
        *,
        chat: typing.Union[str, int, None],
        user: typing.Union[str, int, None],
        data: typing.Dict,
        **kwargs,
    ):
        logging.debug("DBHelper update_data")
        whole_data = self._get_whole_data(chat, user)
        whole_data["data"].update(data, **kwargs)
        self._set_whole_data(chat=chat, user=user, whole_data=whole_data)

    # def add_glpi_id(self, user: typing.Union[str, int, None], glpi_id: int):
    #     with self._database.transaction():
    #         if glpi_id in self._glpi_id:
    #             data = bytes_to_dict(self._glpi_id[glpi_id])
    #         else:
    #             data = []
    #         self._glpi_id[glpi_id] = dict_to_bytes(data + [int(user)])

    # def delete_glpi_id(self, user: typing.Union[str, int, None], glpi_id: int):
    #     with self._database.transaction():
    #         if glpi_id in self._glpi_id:
    #             data = bytes_to_dict(self._glpi_id[glpi_id])
    #         else:
    #             return
    #         try:
    #             data.remove(int(user))
    #         except ValueError:
    #             return
    #         self._glpi_id[glpi_id] = dict_to_bytes(data)

    async def get_bucket(
        self,
        *,
        chat: typing.Union[str, int, None],
        user: typing.Union[str, int, None],
        default: typing.Optional[dict],
    ) -> typing.Dict:
        # TODO under construction
        raise NotImplementedError

    async def set_bucket(
        self,
        *,
        chat: typing.Union[str, int, None],
        user: typing.Union[str, int, None],
        bucket: typing.Dict,
    ):
        # TODO under construction
        raise NotImplementedError

    async def update_bucket(
        self,
        *,
        chat: typing.Union[str, int, None],
        user: typing.Union[str, int, None],
        bucket: typing.Dict,
        **kwargs,
    ):
        # TODO under construction
        raise NotImplementedError
