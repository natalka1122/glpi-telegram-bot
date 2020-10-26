from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    to_enter_login = State()  # Will be represented in storage as 'Form:to_enter_login'
    to_enter_password = State()  # Will be represented in storage as 'Form:to_enter_password'
    logged_in = State()  # Will be represented in storage as 'Form:logged_in'