"""Genetate random quote
"""
import json
import requests


def get_quote():
    """Generate

    Returns:
        [type]: [description]
    """
    url = "http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=ru"
    response = json.loads(requests.request("GET", url, headers={}, data={}).text)
    print(type(response), response)
    quote_author = response["quoteAuthor"]
    quote_text = response["quoteText"]
    if len(quote_author) > 0:
        return f"{quote_text} (c) {quote_author}"
    return quote_text
