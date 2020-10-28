"""Module for every possible state in aiogram
"""
from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    """Class for every possible state in aiogram"""

    to_enter_login = State()  # Will be represented in storage as 'Form:to_enter_login'
    to_enter_password = (
        State()
    )  # Will be represented in storage as 'Form:to_enter_password'
    logged_in = State()  # Will be represented in storage as 'Form:logged_in'
    to_enter_title = State()  # Will be represented in storage as 'Form:to_enter_title'
    to_select_ticket_number = (
        State()
    )  # Will be represented in storage as 'Form:to_select_ticket_number'
    to_select_edit_field = (
        State()
    )  # Will be represented in storage as 'Form:to_select_edit_field'
