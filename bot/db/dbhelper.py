"""Manage comunication with vedis database
"""
import json
from typing import Any
import vedis


class DBHelper:
    """Main class to communicate with vedis
    By default it write to memory, it is recommended to use file instead.
    """

    def __init__(self, filename: str = ":mem:"):
        self._filename: str = filename
        self._database: vedis = vedis.Vedis(self._filename)

    def add_data(self, key: int, value) -> None:
        """Add data to corresponding key

        Args:
            key (int): normally user_id
            value ([type]): user attributes
        """
        with self._database.transaction():
            self._database.set(key, json.dumps(value))

    def add_field(self, key: int, sub_key: str, value: Any) -> None:
        """Add field to database record

        Args:
            key (int): normally user_id
            sub_key (str): user attribute
            value (Any): value if user_attribute
        """
        # TODO Test me
        with self._database.transaction():
            data = json.loads(self._database[key].decode("utf8"))
            data[sub_key] = value
            self._database[key] = json.dumps(data)

    def pop_field(self, key: int, sub_key: str) -> str:
        """Delete and return field to database record

        Args:
            key (int): normally user_id
            sub_key (str): user attribute
            value (Any): value if user_attribute
        """  # TODO Test me
        with self._database.transaction():
            data = json.loads(self._database[key].decode("utf8"))
            result = data[sub_key]
            del data[sub_key]
            self._database[key] = json.dumps(data)
            return result

    def delete_data(self, key: int) -> None:
        """Delete data from corresponding key

        Args:
            key (int): normally user_id
        """
        with self._database.transaction():
            try:
                self._database.delete(key)
            except KeyError:
                pass

    def get_data(self, key: int):
        """Returns data from corresponding key

        Args:
            key (int): normally user_id

        Returns:
            Dict: json with data
        """
        try:
            return json.loads(self._database.get(key).decode("utf8"))
        except KeyError:
            return None
