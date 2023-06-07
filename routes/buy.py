from flask import Blueprint, jsonify, request, session

from application import db
from utils import apology, login_required, lookup

buy_blueprint = Blueprint("buy", __name__)


@buy_blueprint.route("/buy", methods=["PUT"])
@login_required
def buy():
    """Buy shares of stock"""

    # Access form data
    symbol = request.form.get("symbol_buy")
    shares = int(request.form.get("shares_buy"))

    # Access user's id
    user_id = session["user_id"]

    # Ensure symbol was submitted
    if not symbol:
        return apology("must provide symbol", 400)

    # Ensure shares was submitted
    if not shares:
        return apology("must provide shares", 400)

    # Obtain quote using lookup function
    quoted = lookup(symbol)

    # Ensure valid symbol was submitted
    if quoted is None:
        return apology("invalid symbol", 400)

    # Check if user has enough cash to buy shares
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    price = float(quoted[symbol]["currentPrice"])
    price_minor_units = int(price * 100)
    cost = price_minor_units * shares
    if cash < cost:
        # User does not have enough cash to buy shares
        return apology("can't afford", 400)

    # New amount of cash user has after buying shares
    new_cash_total = cash - cost

    # Update cash in users table for user
    db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash_total, user_id)

    # Insert buy log into history table
    db.execute(
        "INSERT INTO history (user_id, symbol, shares, price, transacted)"
        "VALUES (?, ?, ?, ?, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))",
        user_id,
        symbol,
        shares,
        price_minor_units,
    )

    if current_shares := db.execute(
        "SELECT shares_count FROM shares WHERE user_id = ? AND symbol = ?",
        user_id,
        symbol,
    ):
        # Shares have been bought before
        new_shares_total = current_shares[0]["shares_count"] + shares
        shares_value_total = new_shares_total * price_minor_units
        db.execute(
            "UPDATE shares SET shares_count = ?, price = ?, total = ? WHERE user_id = ? AND symbol = ?",
            new_shares_total,
            price_minor_units,
            shares_value_total,
            user_id,
            symbol,
        )

    else:
        # Shares have not been bought before
        name = quoted[symbol]["longName"]
        db.execute(
            "INSERT INTO shares VALUES (?, ?, ?, ?, ?, ?)",
            user_id,
            symbol,
            name,
            shares,
            price_minor_units,
            cost,
        )

    # Return success status
    return jsonify(True)


@buy_blueprint.route("/buy_check")
@login_required
def buy_check():
    """Check if user has enough cash to buy requested amount of shares"""

    # Access user's id
    user_id = session["user_id"]

    # Access form data
    symbol = request.args.get("symbol_buy")
    shares = int(request.args.get("shares_buy"))

    # User did not supply symbol
    if not symbol:
        return jsonify(True)

    # Obtain quote using lookup function
    quoted = lookup(symbol)

    # Check if user has enough cash to buy shares
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    price = float(quoted[symbol]["currentPrice"])
    price_minor_units = int(price * 100)
    cost = price_minor_units * shares
    # Return True if user has enough cash to buy shares, otherwise return False
    return jsonify(True) if cash >= cost else jsonify(False)
