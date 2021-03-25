"""General ticket manipulations
"""
import logging
import typing
import html2text
import html2markdown

from config import GLPI_TICKET_URL

MAX_MESSAGE_LENGTH = 2000
UNKNOWN = "Мама, это какое-то неизвестное науке число"
STATUS = {
    1: "Новый",
    2: "В работе (назначена)",
    3: "В работе (запланирована)",
    4: "Ожидает ответа заявителя",
    5: "Решена",
    6: "Закрыто",
}
URGENCY = {
    # 1: "Очень низкий",
    4: "Высокий",
    2: "Низкий",
    3: "Средний",
    # 5: "Очень высокая",
    -1: "/Отмена",
}


def int_to_status(num: int) -> str:
    """User-friendly status description

    Args:
        num (int): status_id

    Returns:
        str: Status description
    """
    if num in STATUS:
        return STATUS[num]
    return UNKNOWN + ": " + str(num)


def int_to_urgency(num: int) -> str:
    """User-friendly urgency description

    Args:
        num (int): status_id

    Returns:
        str: Urgency description
    """
    if num in URGENCY:
        return URGENCY[num]
    return UNKNOWN + ": " + str(num)


def urgency_to_int(urgency: str) -> int:
    """Convert urgency-description to integer

    Args:
        urgency (str): User-friendly urgency description

    Raises:
        KeyError: If no such urgency

    Returns:
        int: for glpi-system
    """
    for key in URGENCY:
        if URGENCY[key] == urgency:
            return key
    raise KeyError


def show_ticket(
    ticket: typing.Dict,
) -> str:
    """ Show ticket for user """
    logging.info("ticket = %s", ticket)
    content = html2markdown.convert(
        html2text.html2text(str(ticket["content"])))
    result: typing.List = []
    result.append(f"Заявка с номером <a href=\"{GLPI_TICKET_URL}{ticket['id']}\">{ticket['id']} '{ticket['name']}'</a>")
    #.format(ticket["id"], ticket["name"]))
    result.append("Статус: {}".format(int_to_status(ticket["status"])))
    result.append("Срочность: {}".format(int_to_urgency(ticket["urgency"])))
    result.append("Дата открытия: {}".format(ticket["date"]))
    result.append("Содержание: {}".format(content))
    return "\n".join(result)
