from config import SKIT_BASE_URL

import bot.glpi_api as glpi_api
import bot.app.core as core

class AuthenticationError(Exception):
    pass

class UserSession:
    def __init__(self, user_id, login, password):
        self.user_id = user_id
        self.login = login
        self.password = password

        # raise error if no login with provided credentials
        with glpi_api.connect(url=SKIT_BASE_URL, auth=(self.login, self.password), apptoken='', verify_certs=True):
            pass

        core.db_connect.add_data(user_id, {'login': self.login, 'password': self.password})
    
    def get_all_tickers(self):
        with glpi_api.connect(url=SKIT_BASE_URL, auth=(self.login, self.password), apptoken='', verify_certs=True) as glpi:
            return glpi.get_all_items('ticket')
