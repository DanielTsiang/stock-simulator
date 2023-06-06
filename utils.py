from datetime import datetime
from functools import wraps

import requests
import yfinance as yf
from flask import redirect, render_template, session


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
        if isinstance(symbols, list):
            # convert list of symbols into string of symbols with commas
            symbols = ",".join(symbols)

        tickers = yf.Tickers(symbols).tickers
    except requests.RequestException:
        return None

    # Parse response
    try:
        required_fields = ["symbol", "longName", "currentPrice"]

        # Use dict comprehension to create dict to be returned
        return {
            # Use dict comprehension to remove unwanted key value pairs from yfinance.Ticker.info dict
            ticker: {key: tickers[ticker].info[key] for key in required_fields}
            for ticker in tickers
        }
    
    except (KeyError, TypeError, ValueError):
        return None


def all_symbols():
    """Get a list of all valid symbols."""

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
