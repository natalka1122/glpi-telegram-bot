import json
import vedis

class DBHelper:
    def __init__(self, filename: str=':mem:'):
        self.filename: str= filename
        self.db: vedis = vedis.Vedis(self.filename)

    def add_data(self, key, value):
        with self.db.transaction():
            self.db.set(key, json.dumps(value))

    def delete_data(self, key):
        with self.db.transaction():
            try:
                self.db.delete(key)
            except KeyError:
                return -1
        return 0

    def get_data(self, key):
        try:
            return json.loads(self.db.get(key).decode('utf8'))
        except KeyError:
            return None
