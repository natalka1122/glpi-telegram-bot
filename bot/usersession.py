import bot.glpi_api as glpi_api
from bot.app import core

class StupidError(Exception):
    pass

class UserSession:

    URL = core.SKIT_BASE_URL

    def __init__(self, user_id, login=None, password=None):
        data = core.db_connect.get_data(user_id)

        if data is None and (login is None or password is None):
            raise StupidError

        self.user_id = user_id
        if data is None:
            self.login = login
            self.password = password
            self.check_cred()
            core.db_connect.add_data(user_id, {'login': self.login, 'password': self.password})
            return

        self.login = data['login']
        self.password = data['password']
        
    """
    Raise error if no login with provided credentials
    """    
    def check_cred(self):
        with glpi_api.connect(url=self.URL, auth=(self.login, self.password), apptoken=''):
            pass

    def get_all_tickers(self):
        with glpi_api.connect(url=self.URL, auth=(self.login, self.password), apptoken='') as glpi:
            return glpi.get_all_items('ticket')
