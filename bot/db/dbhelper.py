"""Manage comunication with vedis database
"""
import json
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
