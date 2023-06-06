from flask import Blueprint, jsonify, render_template, session

from application import db
from utils import login_required, lookup

index_blueprint = Blueprint("index", __name__)


@index_blueprint.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    return render_template("index.html")


@index_blueprint.route("/index_json")
@login_required
def index_json():
    """Returns JSON data for index page"""

    # Access user's id
    user_id = session["user_id"]

    # Select information from shares table for logged-in user
    shares = db.execute("SELECT * FROM shares WHERE user_id = ?", user_id)

    # List comprehension to convert list of dicts into list of symbols
    symbols_owned = [share["symbol"] for share in shares]

    # Obtain the latest share price(s) from API and update database
    quoted = lookup(symbols_owned)

    for share in shares:
        price = float(quoted[share["symbol"]]["currentPrice"])
        price_minor_units = int(price * 100)
        new_shares_total = share["shares_count"] * price_minor_units
        db.execute(
            "UPDATE shares SET price = ?, total = ? WHERE user_id = ? AND symbol = ?",
            price_minor_units,
            new_shares_total,
            user_id,
            share["symbol"],
        )
        share["price"] = price
        share["total"] = new_shares_total / 100

    # Check how much cash the user currently has
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    cash_major_units = cash / 100

    return jsonify({"shares_data": shares, "cash_data": cash_major_units})
