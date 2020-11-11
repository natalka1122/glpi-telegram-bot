"""Genetate random quote
"""
import json
import typing
import requests


def get_quote() -> str:
    """Get random quote from https://forismatic.com

    Returns:
        str: [description]
    """
    url: str = "http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=ru"
    response: typing.Dict = json.loads(
        requests.request("GET", url, headers={}, data={}).text
    )
    quote_author: str = response["quoteAuthor"]
    quote_text: str = response["quoteText"]
    if len(quote_author) > 0:
        return f"{quote_text} (c) {quote_author}"
    return quote_text
