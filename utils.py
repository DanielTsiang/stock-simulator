import os
import requests
import urllib.parse

from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return (
        render_template("apology.html", top=f"{code} error", bottom=escape(message)),
        code,
    )


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbols):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        if type(symbols) is list:
            # convert list of symbols into string of symbols with commas
            symbols = ",".join(symbols)
        url = f"https://cloud.iexapis.com/stable/stock/market/batch?symbols={urllib.parse.quote_plus(symbols)}&types=quote&filter=symbol,companyName,latestPrice&token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        return response.json()
    except (KeyError, TypeError, ValueError):
        return None


def all_symbols():
    """Get a list of all valid IEX symbols."""

    # Get JSON data from url
    try:
        url = "https://iextrading.com/api/mobile/refdata"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        symbols_data = response.json()
        # Use dict comprehension inisde a list comprehension to remove unwanted key value pairs from list of dictionaries
        symbols_data_stripped = [
            {key: value for key, value in data.items() if key in ["Symbol", "Issuer"]}
            for data in symbols_data
        ]

        # Use dict compresion inside a list comprehension to remove unwanted key value pairs from list of dictionaries
        symbols_only_data = [
            {key: value for key, value in data.items() if key == "Symbol"}
            for data in symbols_data
        ]

        # List comprehension to convert list of dicts into list of "Symbols"
        symbols_list = [symbol["Symbol"] for symbol in symbols_data]

        return symbols_data_stripped, symbols_only_data, symbols_list
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value / 100:,.2f}"


def datetimeformat(dt_string, format="%d-%m-%Y %H:%M:%S"):
    dt_object = datetime.strptime(str(dt_string), "%Y-%m-%d %H:%M:%S")
    return dt_object.strftime(format)
