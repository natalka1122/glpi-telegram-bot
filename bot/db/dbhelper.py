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
    return json.loads(source.decode("utf8"))


def dict_to_bytes(source: typing.Dict) -> bytes:
    """Converts dict into bytes

    Args:
        source (typing.Dict): Source dict

    Returns:
        bytes: Resulting string in bytes
    """
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
        self._login: vedis.Hash = self._database.Hash("login")

    async def close(self):
        logging.debug("DBHelper close")
        self.debug()
        self._database.close()

    async def wait_closed(self):
        logging.debug("DBHelper wait_closed")
        # pass

    def debug(self) -> None:
        """Prints database content"""
        logging.debug("DBHelper debug")
        with self._database.transaction():
            logging.info("user_id: %s", self._userid.to_dict())
            logging.info("login: %s", self._login.to_dict())

    def resolve_address(self, chat: int, user: int) -> str:
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
        user = self.resolve_address(chat=chat, user=user)
        with self._database.transaction():
            whole_data: typing.Dict = bytes_to_dict(self._userid[user])
        logging.info("whole_data: %s", whole_data)
        return whole_data

    def _set_whole_data(
        self,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        whole_data: typing.Dict = None,
    ) -> None:
        # TODO write docstring
        """[summary]

        Args:
            chat (typing.Union[str, int, None], optional): [description]. Defaults to None.
            user (typing.Union[str, int, None], optional): [description]. Defaults to None.
            data (typing.Dict, optional): [description]. Defaults to None.
        """
        if whole_data is None:
            whole_data = {}
        user = self.resolve_address(chat=chat, user=user)
        with self._database.transaction():
            self._userid[user] = dict_to_bytes(whole_data)

    async def get_state(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        default: typing.Optional[str] = None,
    ) -> typing.Optional[str]:
        logging.info("DBHelper get_state")
        return self._get_whole_data(chat=chat, user=user).get(STATE, default)

    async def set_state(
        self,
        *,
        chat: typing.Union[str, int, None],
        user: typing.Union[str, int, None],
        state: typing.Optional[typing.AnyStr],
    ):
        logging.info("DBHelper set_state %s", state)
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
        logging.info("DBHelper get_data")
        return self._get_whole_data(chat, user).get(DATA, default)

    async def set_data(
        self,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        data: typing.Dict,
    ):
        logging.info("DBHelper set_data")
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
        logging.info("DBHelper update_data")
        whole_data = self._get_whole_data(chat, user)
        whole_data["data"].update(data, **kwargs)
        self._set_whole_data(chat=chat, user=user, whole_data=whole_data)

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

    # def add_data(self, user_id: int, data: Dict) -> None:
    #     """Add data to corresponding key

    #    Args:
    #        user_id (int): telegram
    #        value ([type]): user attributes
    #    """
    #    with self._database.transaction():
    #        self._userid.set(user_id, json.dumps(data))
    #        if "login" in data:
    #            self._login[data["login"]] = user_id

    # def add_field(self, key: int, sub_key: str, value: str) -> None:
    #    """Add field to database record

    #    Args:
    #        key (int): normally user_id
    #        sub_key (str): user attribute
    #        value (Any): value if user_attribute
    #    """
    #    # TODO Test me
    #    with self._database.transaction():
    #        data = json.loads(self._database[key].decode("utf8"))
    #        data[sub_key] = value
    #        self._database[key] = json.dumps(data)

    # def pop_field(self, key: int, sub_key: str) -> str:
    #    """Delete and return field to database record

    #    Args:
    #        key (int): normally user_id
    #        sub_key (str): user attribute
    #        value (Any): value if user_attribute
    #    """  # TODO Test me
    #    with self._database.transaction():
    #        data = json.loads(self._database[key].decode("utf8"))
    #        result = data[sub_key]
    #        del data[sub_key]
    #        self._database[key] = json.dumps(data)
    #        return result

    # def delete_data(self, key: int) -> None:
    #    """Delete data from corresponding key

    #    Args:
    #        key (int): normally user_id
    #    """
    #    with self._database.transaction():
    #        try:
    #            self._database.delete(key)
    #        except KeyError:
    #            pass

    # def get_data(self, key: int):
    #    """Returns data from corresponding key

    #    Args:
    #        key (int): normally user_id

    #    Returns:
    #        Dict: json with data
    #    """
    #    try:
    #        return json.loads(self._database.get(key).decode("utf8"))
    #    except KeyError:
    #        return None
