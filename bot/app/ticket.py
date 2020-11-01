"""General ticket manipulations
"""
from typing import Dict, List, Callable
from html2text import html2text

MAX_MESSAGE_LENGTH = 2000
UNKNOWN = "Мама, это какое-то неизвестное науке число"
STATUS = {1: "Новый", 2: "В работе"}
URGENCY = {
    1: "Очень низкий",
    2: "Низкий",
    3: "Средний",
    4: "Высокая",
    5: "Очень высокая",
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


async def show_ticket(
    ticket: Dict, send_message: Callable, user_id, max_len: int = MAX_MESSAGE_LENGTH
) -> None:
    """Show ticket in chunks when needed"""
    result: List = []
    result.append("Заявка с номером {} '{}'".format(ticket["id"], ticket["name"]))
    result.append("Статус: {}".format(int_to_status(ticket["status"])))
    result.append("Срочность: {}".format(int_to_urgency(ticket["urgency"])))
    result.append("Дата открытия: {}".format(ticket["date"]))
    # TODO: Fix <p> and may be somethings more
    result.append("Содержание: {}".format(html2text(ticket["content"])))

    buffer = ""
    for line in result:
        line = str.strip(line)
        if len(buffer + line) <= max_len:
            if len(buffer) == 0:
                buffer = line
            else:
                buffer += "\n" + line
            continue

        # len(buffer) + line > max_len
        if len(buffer) > 0:
            await send_message(user_id, buffer)
        if len(line) < max_len:
            buffer = line
            continue

        # len(line) > max_len
        buffer = ""
        while len(line) > max_len:
            chunk = str.strip(line[:max_len])
            if len(chunk) > 0:
                await send_message(user_id, chunk)
            line = str.strip(line[max_len:])

        if len(line) > 0:
            await send_message(user_id, line)


    if len(buffer) > 0:
        await send_message(user_id, buffer)
