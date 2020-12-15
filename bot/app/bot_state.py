"""Module for every possible state in aiogram
"""
from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    """Class for every possible state in aiogram"""

    to_enter_login = State()  # 'Form:to_enter_login'
    to_enter_password = State()  # 'Form:to_enter_password'
    logged_in = State()  # 'Form:logged_in'

    to_select_category = State()  # 'Form:to_select_category'
    to_enter_title = State()  # 'Form:to_enter_title'
    to_enter_description = State()  # 'Form:to_enter_description'
    to_select_priority = State()  # 'Form:to_select_priority'

    to_explain_decline = State()  # 'Form:to_explain_decline'
