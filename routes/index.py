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
    SHARES = db.execute("SELECT * FROM shares WHERE user_id = ?", user_id)

    # List comprehension to convert list of dicts into list of symbols
    symbols_owned = [share["symbol"] for share in SHARES]

    # Obtain the latest share price(s) from API and update database
    QUOTED = lookup(symbols_owned)

    for share in SHARES:
        price = float(QUOTED[share["symbol"]]["quote"]["latestPrice"])
        new_shares_total = share["shares_count"] * float(
            QUOTED[share["symbol"]]["quote"]["latestPrice"]
        )
        db.execute(
            "UPDATE shares SET price = ?, total = ? WHERE user_id = ? AND symbol = ?",
            price,
            new_shares_total,
            user_id,
            share["symbol"],
        )
        share["price"] = price
        share["total"] = new_shares_total

    # Check how much cash the user currently has
    CASH = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    return jsonify({"shares_data": SHARES, "cash_data": CASH})
